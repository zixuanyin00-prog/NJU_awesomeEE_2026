# 电子基础学实验 2 · ADC 与串口

在 STM32F429IGT6 上用 ADC1 采集 PC2 的输入，借助板载 DAP-Link 的虚拟串口将结果送到电脑。程序默认每 5 ms 采样一次（标称 200 Hz），每行输出 `ADC 原始值,毫伏值`。ADC 为 12 位，电压换算按 3300 mV 参考电压估算。

## Windows 环境部署

1. 安装 Keil MDK 5。本工程使用 Keil 5.39 和 Arm Compiler 6.21。在 Pack Installer 中安装 `Keil::STM32F4xx_DFP 2.17.1` 和工程引用的 `ARM::CMSIS 4.5.0`。 [Keil MDK 下载](https://www.keil.com/download/product/) · [STM32F4xx 设备包版本](https://www.keil.arm.com/packs/stm32f4xx_dfp-keil/versions/)
2. 用 Keil 打开 [STM32F429_UART_ADC.uvprojx](MDK-ARM/STM32F429_UART_ADC.uvprojx)，按 F7 编译。Windows PowerShell 也可在本目录运行 `.\build.ps1`。Keil 安装在其他目录时，可用 `.\build.ps1 -Uv4 'D:\Keil_v5\UV4\UV4.exe'` 或设置 `KEIL_UV4`。新编译的 HEX 位于 `MDK-ARM/STM32F429_UART_ADC/`，已归档的 HEX 位于 [firmware](firmware/)。
3. 查看或修改引脚配置时，用 STM32CubeMX 打开 [STM32F429_UART_ADC.ioc](STM32F429_UART_ADC.ioc)。配置使用 CubeMX 6.8.1 和 STM32CubeF4 1.27.1，HAL 和 CMSIS 源码已随项目归档。业务代码位于 [main.c](Core/Src/main.c) 的 `USER CODE` 区。若重新生成代码，请先备份 Keil 工程文件和应用源码，并检查编译器、启动文件和烧录配置。 [STM32CubeMX](https://www.st.com/en/development-tools/stm32cubemx.html) · [STM32CubeF4](https://www.st.com/en/embedded-software/stm32cubef4.html)
4. 可用 VS Code 打开本目录，按 Ctrl+Shift+B 调用同一个 Keil 构建脚本。扩展建议包含 C/C++、Serial Monitor 和 EIDE。如果使用 EIDE，可以导入本目录的 Keil 工程，并选择 Arm Compiler 6。 [EIDE](https://marketplace.visualstudio.com/items?itemName=CL.eide) · [Serial Monitor](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-serial-monitor)

## 烧录和验收

1. 用支持数据传输的 USB 线连接板载 DAP-Link。在 Keil 里使用 CMSIS-DAP Debugger，点击 **LOAD**，完成后运行或复位开发板。Windows 10/11 通常会自动识别 USB 虚拟串口。 [DAP-Link](https://daplink.io/)
2. 在 COMTransmit 或 VS Code Serial Monitor 中打开板子的 COM 口。使用 **115200 波特、8 数据位、1 停止位、无校验、无流控**，文本收发。串口使用 USART3，PB10 为 TX，PB11 为 RX。
3. 信号源地接板上 GND，输出接 **JD2 第 6 脚（PC2 / ADC1_IN12）**。先用示波器确认实际输入全程在 **0～3.3 V** 内，再接到 ADC。比如设置 5 Hz 正弦、2 Vpp、偏置 +1 V，预期输入为 0～2 V。约 1.65 V 的直流输入在理想条件下应显示接近 `2048,1650`。
4. 测串口回显时，关闭发送自动换行，单独发 `-` 暂停采集，然后一次发送一小段文本，如 `hello`，检查回传是否一致。单独发 `+` 恢复采集。

Keil 构建已通过，结果为 0 错误、0 警告。采样率、电压和串口行为等待实板验收。第三方源码授权随 [Package_license.md](Package_license.md) 和 Drivers 内的许可证文件归档。Keil、CubeMX 和串口助手从各自官网安装。
