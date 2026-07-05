# Linux 自动化日志备份 Shell 脚本
## 项目简介
基于WSL2 Ubuntu开发的日志自动备份工具，用于批量归档程序运行日志，自动给备份文件追加日期后缀，解决日志覆盖问题，适配AI Agent、后端服务日常运维场景。
## 技术栈
Linux Shell、awk、grep、WSL2 Ubuntu
## 文件说明
1. backup.sh：核心备份脚本（带完整注释）
2. run_success.png：脚本运行成功终端截图
3. backup_file_list.png：备份生成文件验证截图
## 运行操作步骤
1. 初始化测试日志目录
mkdir -p ~/logs ~/backup
cd ~/logs
echo "2024-07-03 INFO: System started" > app.log
echo "2024-07-03 ERROR: Connection failed" > error.log
echo "2024-07-03 INFO: User login" > access.log
2. 赋予脚本执行权限
chmod +x backup.sh
3. 执行备份脚本
./backup.sh
4. 查看备份结果
ls ~/backup
## 实操踩坑汇总
1. 问题：执行 cd ~/AI_Agent_Study 持续报错：No such file or directory
解决：WSL 访问 Windows 桌面固定前缀：/mnt/c/Users/administrator/Desktop/AI_Agent_Study/对应子目录
心得：Windows 本地文件夹，WSL 只能通过/mnt/c/挂载路径进入；~/ 仅限 Ubuntu 内部文件使用，二者路径不能混用
2. 问题：git commit 执行失败，提示：Author identity unknown、空用户名不允许提交
解决：首次使用 Git，需配置全局提交用户名、绑定 GitHub 注册邮箱，Git 无法识别提交者身份，阻断 commit 流程
心得：全局配置仅需要执行一次，后续所有 Git 项目永久生效；commit 必须提前配置身份信息
