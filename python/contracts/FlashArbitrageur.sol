// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title FlashArbitrageur
 * @notice Контракт-исполнитель флеш-арбитража.
 *         Вызывается Python-скриптом. Внутри executeOperation()
 *         делает swap на втором DEX и возвращает средства + комиссию.
 *
 * @dev    Для Sepolia testnet — упрощённая версия без реальных DEX-интеграций.
 *         В продакшене подключаются Uniswap V3 Router, SushiSwap Router и т.д.
 */

import "@aave/v3-core/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "@aave/v3-core/contracts/interfaces/IPoolAddressesProvider.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract FlashArbitrageur is FlashLoanSimpleReceiverBase {
    address public owner;

    // Роутеры DEX (заполняются при деплое на Sepolia)
    address public uniswapRouter;
    address public sushiRouter;

    event ArbitrageExecuted(
        address indexed token,
        uint256 profit,
        address buyDex,
        address sellDex
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyPool() {
        require(msg.sender == address(POOL), "Not pool");
        _;
    }

    constructor(address _addressProvider) 
        FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_addressProvider)) 
    {
        owner = msg.sender;
    }

    /**
     * @notice Запуск флеш-арбитража извне (Python вызывает эту функцию).
     * @param asset          Токен займа (WETH на Sepolia)
     * @param amount         Сумма займа
     * @param buyDex         Адрес DEX для покупки
     * @param sellDex        Адрес DEX для продажи
     */
    function executeArbitrage(
        address asset,
        uint256 amount,
        address buyDex,
        address sellDex
    ) external onlyOwner {
        bytes memory params = abi.encode(buyDex, sellDex);
        POOL.flashLoanSimple(address(this), asset, amount, params, 0);
    }

    /**
     * @notice Коллбэк от Aave — сюда приходят заёмные средства.
     *         Внутри делаем swap и возвращаем займ + комиссию.
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override onlyPool returns (bool) {
        (address buyDex, address sellDex) = abi.decode(params, (address, address));

        // 1. Swap на первом DEX (покупаем целевой токен)
        //    В реальности — вызов IUniswapV3Router.exactInputSingle()
        //    Здесь — заглушка для Sepolia

        // 2. Swap на втором DEX (продаём обратно в ETH/WETH)
        //    В реальности — вызов ISushiRouter.swapExactTokensForETH()

        // 3. Возврат займа + premium
        uint256 amountOwed = amount + premium;
        IERC20(asset).approve(address(POOL), amountOwed);

        // Прибыль остаётся в контракте
        uint256 profit = IERC20(asset).balanceOf(address(this)) - amountOwed;

        emit ArbitrageExecuted(asset, profit, buyDex, sellDex);
        return true;
    }

    /**
     * @notice Вывод прибыли владельцем.
     */
    function withdraw(address token) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        require(balance > 0, "No balance");
        IERC20(token).transfer(owner, balance);
    }

    /**
     * @notice Вывод ETH.
     */
    function withdrawETH() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }

    receive() external payable {}
}
