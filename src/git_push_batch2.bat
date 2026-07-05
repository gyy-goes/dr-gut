@echo off
chcp 65001 >nul
:: ==============================================
:: 批次2 四大核心行业模块 开源存证提交脚本
:: 版本标签：v0.2-Core4Industry
:: ==============================================

echo === 检查当前工作区状态 ===
git status

echo.
echo === 暂存批次2所有文件 ===
git add Medical-CT/
git add Medical-Ultrasound/
git add Geo-MountainNav/
git add Ocean-SubNav/
git add requirements.txt
git add docs/Repository_Structure.md
git add README.md

echo.
echo === 提交批次2内容 ===
git commit -m "feat(batch2): 新增四大成熟核心行业模块（Medical-CT/超声、山区导航、水下测绘）
- 所有模块统一复用Common-LSG底层接口，无重复核心逻辑
- 每个模块包含场景约束、噪声优化、硬件适配、Demo示例四件套
- 补充完整场景README与开源声明
- 更新全仓库依赖清单与目录结构文档
- 版本标签：v0.2-Core4Industry"

echo.
echo === 打版本标签 v0.2-Core4Industry ===
git tag -a v0.2-Core4Industry -m "LSG v0.2 四大核心行业模块正式开源存证，覆盖医疗影像、空对地、水下测绘三大赛道"

echo.
echo === 推送代码与标签至远程 ===
git push origin main
git push origin v0.2-Core4Industry

echo.
echo ✅ 批次2提交完成，远程永久存证成功！
echo 版本标签：v0.2-Core4Industry
pause