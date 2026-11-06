# 电子基础学实验 2 · ADC 与串口

STM32F429IGT6 用 ADC1 的单个通道采集 PC2。TIM2 的更新事件通过 TRGO 触发转换，DMA2 Stream 0 Channel 0 以循环模式把 12 位结果搬到内存。TIM2 时钟为 16 MHz，预分频值为 79，自动重装值为 999，采样率标称为 200 Hz。USART1 把样本发给电脑上的 COMTransmit，每行是 `样本序号,ADC 原始值,毫伏值`。电压按 3300 mV 参考电压估算。

## Windows 环境部署

1. 安装 Keil MDK 5。本工程使用 Keil 5.39 和 Arm Compiler 6.21。在 Pack Installer 中安装 `Keil::STM32F4xx_DFP 2.17.1` 和工程引用的 `ARM::CMSIS 4.5.0`。 [Keil MDK 下载](https://www.keil.com/download/product/) · [STM32F4xx 设备包版本](https://www.keil.arm.com/packs/stm32f4xx_dfp-keil/versions/)
2. 用 Keil 打开 [STM32F429_UART_ADC.uvprojx](MDK-ARM/STM32F429_UART_ADC.uvprojx)，按 F7 编译。Windows PowerShell 也可在本目录运行 `.\build.ps1`。Keil 安装在其他目录时，可用 `.\build.ps1 -Uv4 'D:\Keil_v5\UV4\UV4.exe'` 或设置 `KEIL_UV4`。新编译的 HEX 位于 `MDK-ARM/STM32F429_UART_ADC/`，已归档的 HEX 位于 [firmware](firmware/)。
3. 查看或修改引脚配置时，用 STM32CubeMX 打开 [STM32F429_UART_ADC.ioc](STM32F429_UART_ADC.ioc)。配置使用 CubeMX 6.8.1 和 STM32CubeF4 1.27.1，HAL 和 CMSIS 源码已随项目归档。业务代码位于 [main.c](Core/Src/main.c) 的 `USER CODE` 区。若重新生成代码，请先备份 Keil 工程文件和应用源码，并检查编译器、启动文件和烧录配置。 [STM32CubeMX](https://www.st.com/en/development-tools/stm32cubemx.html) · [STM32CubeF4](https://www.st.com/en/embedded-software/stm32cubef4.html)
4. 可用 VS Code 打开本目录，按 Ctrl+Shift+B 调用同一个 Keil 构建脚本。如果使用 EIDE，可以导入本目录的 Keil 工程，并选择 Arm Compiler 6。 [EIDE](https://marketplace.visualstudio.com/items?itemName=CL.eide)

## 烧录和 COMTransmit 接线

1. 用支持数据传输的 USB 线连接板载 DAP-Link。在 Keil 里使用 CMSIS-DAP Debugger，点击 **LOAD**，完成后运行或复位开发板。
2. 用 **3.3 V 电平的 USB 转 TTL** 接 USART1。开发板由 DAP-Link USB 供电，转接器接以下三根线。

   | 开发板 JD2 | USB 转 TTL |
   |---|---|
   | 第 7 脚 PA9 / USART1_TX | RXD |
   | 第 5 脚 PA10 / USART1_RX | TXD |
   | 第 3 脚 GND | GND |

3. 在 **COMTransmit** 中选择 USB 转 TTL 对应的 COM 口。使用 **115200 波特、8 数据位、1 停止位、无校验、无流控**，收发选择文本，接收日志关闭时间戳和方向前缀。 [COMTransmit 官方下载](https://www.wch.cn/downloads/COMTransmit_ZIP.html)
4. 信号源地接板上 GND，输出接 **JD2 第 6 脚（PC2 / ADC1_IN12）**。接入前用示波器确认实际波形始终在 **0～3.3 V** 内。
5. 测串口回显时，关闭发送自动追加换行，单独发 `-` 暂停采样数据输出，发送 `hello` 检查回传，再单独发 `+` 恢复输出。保存测量数据时，取一段连续的采集输出。

## 课堂验收

- **3.1 直流**。输入已用万用表核对的直流电压，例如约 1.65 V。在 COMTransmit 中查看第三列是否接近 1650 mV，保存连续的纯文本数据为 `dc.csv`，记录万用表读数并与 ADC 平均值比较。
- **3.2 交流**。可使用 5 Hz 正弦波、2 Vpp、+1 V 偏置。用示波器确认接入前的实际输入范围，保存至少 2 秒连续数据为 `ac.csv`，便于从任意起始相位截取两个完整周期。导出仅保留完整的 `序号,原始值,毫伏值` 行。

安装 Matplotlib 后，在本目录运行以下命令。分析脚本校验样本序号连续性，生成 PNG 和文本分析。交流模式用同向过零点确认完整周期，并报告周期、频率、峰峰值和偏置估计。

```powershell
python -m pip install matplotlib
python analyze_adc.py dc.csv --mode dc
python analyze_adc.py ac.csv --mode ac
```

Keil 构建结果为 0 错误、0 警告。直流读数和交流采集结果等待烧录后的实板验收。第三方源码授权随 [Package_license.md](Package_license.md) 和 Drivers 内的许可证文件归档。
