# 词典笔 - 系统镜像资源

本仓库用于存放词典笔相关的系统固件资源，包括根文件系统（rootfs），启动镜像（boot）和OTA更新包。

## 资源下载

所有镜像文件均发布在 **Releases** 页面，请前往以下地址下载：

👉 [Releases 页面](https://github.com/lbdl0030/dictpen-rootfs/releases)

## 文件说明

| 文件类型 | 说明 | 注意事项 |
|---------|------|----------|
| rootfs | 根文件系统镜像 | **未改写读写权限** |
| boot | 启动分区镜像 | 包含内核及启动相关文件 |
| OTA | 词典笔OS更新包 | 包含增量更新包和全量更新包，注意新发布的部分OTA包不按照设备型号分类，详情请看**重要提示** |

> ⚠️ **重要提醒**：请务必根据 Release 标题和说明中的标注选择对应版本，不同机型/固件版本可能存在差异。使用部分新发布的OTA时，您应该先确认您的设备树模型，再根据设备树模型映射表使用对应的OTA更新包并注意您想要的OS版本。

---

## 如何确认您的设备型号

在词典笔上执行以下命令（可通过 ADB Shell 或终端模拟器）：

```bash
cat /proc/device-tree/model
```

输出示例：

```text
Rockchip RK3566 Youdao CHERRY Board
```

将输出结果与下方的设备树模型映射表进行对照，即可找到对应的内部代号，然后在 Releases 页面中选择匹配的 OTA 包。

---

## 设备树模型 → 内部代号映射表

本表列出了本仓库 OTA 包中可能包含的设备树模型（`dts_model`）及其对应的内部代号（`Hardware_type`）。**Releases 中将使用内部代号进行标注**，请根据您的设备树模型查找对应的代号，再下载匹配的固件包。

> **如何获取设备树模型**：在词典笔终端执行 `cat /proc/device-tree/model`，将输出结果与下表对照。


### Rockchip RK3566 平台

| 设备树模型 | 代号 | 型号 |
|-----------|----------|----------|
| `Rockchip RK3566 Youdao CHERRY Board` | `Cherry-3566` | `X3s``X6plus` |
| `Rockchip RK3566 Youdao CHERRY LP4 Board` | `Cherry-3566` | `-` |
| `Rockchip RK3566 Youdao CHERRY LP4 HUSB311 Board` | `Cherry-3566` | `-` |
| `Rockchip RK3566 Youdao CHERRY LPDDR3 Husb311 Board` | `Cherry-3566` | `X3s` |
| `Rockchip RK3566 Youdao CHERRY Mobiiot V10` | `Cherry-3566-mobiiot` | `-` |
| `Rockchip rk3566 for Youdao Kiwi V0 version` | `Kiwi-3566` | `-` |
| `Rockchip RK3566 Youdao Almond Board` | `Almond` | `-` |
| `Rockchip RK3566 Youdao Almond V2 Board` | `Almond` | `-` |


### Rockchip RK3562 平台

| 设备树模型 | 代号 | 型号 |
|-----------|----------|----------|
| `Rockchip RK3562 ORANGE LP4 V10 Board` | `RK3562_Orange` | `X7` |
| `Rockchip RK3562 MELON LP4 V10 Board` | `RK3562_Melon` | `-` |
| `Rockchip RK3562 OLIVE LP4 V10 Board` | `RK3562_Olive` | `-` |
| `Rockchip RK3562 Y02 LP4 V10 Board` | `RK3562_Y02` | `-` |
| `Rockchip RK3562 Y02-1 LP4 V10 Board` | `RK3562_Y02-1` | `-` |
| `Rockchip RK3562 Y03 LP4 V10 Board` | `RK3562_Y03` | `-` |
| `Rockchip RK3562 Y07 LP4 V10 Board` | `RK3562_Y07` | `-` |
| `Rockchip RK3562 POPCORN LP4 V10 Board` | `RK3562_Popcorn` | `-` |


### Rockchip RK3326 平台

| 设备树模型 | 代号 | 型号 |
|-----------|----------|----------|
| `Rockchip rk3326 evb lpddr3 v10 board for linux` | `Dictpen2.0` | `X6plus` |
| `Rockchip rk3326 for Youdao v5 version` | `Dictpen2.0` | `X6plus` |
| `Rockchip rk3326 for Youdao Cherry V0 version` | `Cherry` | `X6plus` |
| `Rockchip rk3326 for Youdao Cherry Husb311 version` | `Cherry` | `-` |
| `Rockchip rk3326 for Youdao Kiwi V0 version` | `Kiwi-3326` | `-` |
| `Rockchip rk3326 for mango version` | `Mango` | `-` |
| `Rockchip rk3326 for apollo version` | `Apollo` | `-` |
| `Rockchip rk3326 for apollo Husb311 version` | `Apollo` | `-` |
| `Rockchip rk3326 for apollo pro version` | `Apollo_Pro` | `-` |
| `Rockchip rk3326 for apollo Husb311 pro version` | `Apollo_Pro` | `-` |
| `Rockchip rk3326 for hermes version` | `Hermes` | `-` |
| `Rockchip rk3326 for hermes Husb311 version` | `Hermes` | `-` |
| `Rockchip rk3326 for exam version` | `Exam` | `-` |
| `Rockchip rk3326 for exam husb311 version` | `Exam` | `-` |
| `Rockchip RK3326S Y05 LP4 V10 Board` | `RK3326S_Y05` | `-` |


### Cvitek CV1826 平台

| 设备树模型 | 代号 | 型号 |
|-----------|----------|----------|
| `Cvitek Cv1826 for Youdao Cherry V0 version` | `Cherry_Cvitek_1826` | `-` |
| `Cvitek Cv1826 for Youdao Cherry V1 5G version` | `Cherry_Cvitek_1826` | `-` |
| `Cvitek Cv1826 for Youdao Melon V0 version` | `CV1826_Melon` | `-` |
| `Cvitek Cv1826 for Youdao PineApple V0 version` | `PineApple` | `-` |
| `Cvitek Cv1826 for Youdao Plum V0 version` | `Plum` | `-` |
| `Cvitek Cv1826 for Youdao Y08 V0 version` | `Y08_CV1813` | `-` |


### Rockchip RV1106 平台

| 设备树模型 | 代号 | 型号 |
|-----------|----------|----------|
| `Rockchip RV1106 for Hermes V10 Board` | `Hermes` | `-` |
| `Rockchip RV1106 for Hermes V1 Board` | `Hermes` | `-` |
| `Rockchip RV1106 for Peach V10 Board` | `Peach_RV1106` | `-` |
| `Rockchip RV1106 for Peach Demo V10 Board` | `Peach_Demo_RV1106` | `-` |
| `Rockchip RV1106 for Pear V10 Board` | `Pear_RV1106` | `A6pro` |
| `Rockchip RV1106 for Y09 V10 Board` | `Y09_RV1106` | `-` |
| `Rockchip RV1106 for Y09P V10 Board` | `Y09P_RV1106` | `-` |
| `Rockchip RV1106 for Y11 Board` | `Y11_RV1106` | `-` |
| `Rockchip RV1106 for Y24 V0 Board` | `Y24_RV1106` | `-` |
| `Rockchip RV1106G Y06 Board` | `Y06_RV1106` | `-` |


### 特殊说明

- **相同代号，不同芯片**：部分代号（如 `Cherry`、`Kiwi`、`Apollo`、`Hermes`）会出现在多个芯片平台上，匹配时需同时检查芯片型号。
- **PCB 版本后缀**：`V0`、`V1`、`V4`、`V5` 等表示硬件 PCB 迭代版本，通常不影响主型号判断。
- **工程代号**：`Y02`、`Y03`、`Y05`、`Y06`、`Y07`、`Y08`、`Y09`、`Y11`、`Y24` 等为内部工程代号，对应市售型号未知。
- **未知型号**：`Almond`、`Mango`、`Melon`、`Olive`、`Orange`、`Popcorn`、`PineApple`、`Plum`、`Peach`、`Pear`、`Hermes` 等代号暂无对应的市售型号确认信息。

---

免责声明

· 请勿用于商业用途，下载后请于24小时内删除。
· Release 发布的镜像仅供参考，使用前请自行评估。因使用本仓库镜像导致的问题，本人概不负责。
· 本仓库提供的固件镜像仅供个人学习、技术研究及设备维修使用。
· 所有文件的版权归原始权利人 网易有道 所有。
· 如果你版权方认为该仓库侵犯了您的权益，请直接联系本人（或通过 GitHub 提交 DMCA 请求）。

问题反馈

如遇到镜像相关问题，请提交 Issue。若您有意愿提供您的设备型号设备树信息和内部代号，请提交Issue，这将帮助我们完善映射表信息

更新说明

目前部分镜像的格式信息尚未完善（如 OTA 包），我会持续对已发布的 Release 进行补充和修正，感谢理解。

1. 修改了release的标题命名，固件包统一为firmware
2. 更新部分OTA分类逻辑和设备树模型映射表

