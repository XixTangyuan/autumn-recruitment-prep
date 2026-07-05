#!/bin/bash
# 脚本名称：log_auto_backup.sh
# 功能：自动批量备份指定目录下所有.log日志文件，文件名追加当日日期防止覆盖
# 运行环境：WSL2 Ubuntu / Linux
# 学习用途：秋招Linux+Shell自动化实操项目，用于简历项目展示
# 执行前置：chmod +x backup.sh 赋予脚本执行权限
# 运行命令：./backup.sh

#################### 1. 全局变量定义区 ####################
# 日志源目录：存放原始待备份日志文件
SOURCE_DIR=~/logs
# 备份存放目录：所有带日期后缀的备份文件统一存放这里
BACKUP_DIR=~/backup
# 获取系统当前日期，格式：年年年年月月日日 例：20260703
# $()为命令替换语法，将date命令输出结果赋值给DATE变量
DATE=$(date +%Y%m%d)

#################### 2. 环境初始化 ####################
# mkdir -p 作用：目录不存在则创建，目录已存在不会抛出报错，兼容重复执行脚本
mkdir -p $BACKUP_DIR

#################### 3. 循环批量备份逻辑 ####################
# for循环遍历源目录下所有后缀为.log的文件
# $SOURCE_DIR/*.log 通配符匹配所有日志文件
for file in $SOURCE_DIR/*.log; do
    # basename 命令：剥离文件完整路径，仅保留纯文件名 例：/home/xxx/logs/app.log → app.log
    filename=$(basename $file)
    
    # 字符串截取语法 ${变量%.后缀}：删除文件名末尾的.log后缀
    # 例：app.log → app，后续拼接日期与新后缀
    new_filename="${filename%.log}_${DATE}.log"

    # 核心操作：复制原始日志文件到备份目录，使用拼接好的带日期新文件名
    cp "$file" "$BACKUP_DIR/$new_filename"

    # 控制台输出日志，告知用户当前哪个文件备份完成，方便排查运行状态
    echo "✅ 已完成备份：$filename  | 备份文件名：$new_filename"
done

#################### 4. 脚本收尾提示 ####################
echo -e "\n==================== 全部日志备份任务执行完毕 ===================="
echo "备份文件存放路径：$BACKUP_DIR"
echo "可输入 ls $BACKUP_DIR 查看所有备份文件"


