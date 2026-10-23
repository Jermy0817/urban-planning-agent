from pathlib import Path
from core import Passage, report
if __name__ == '__main__':
    project=[Passage('模拟任务书.txt','第 1 行','社区更新项目用地面积 12 亩，建筑面积 8000 平方米，总投资 3000 万元。建设内容：改造社区服务中心。')]
    experience=[Passage('模拟经验.txt','第 1 行','社区服务中心经验：先访谈居民，再确定功能；尽早明确运营单位，避免重建设轻运营。')]
    folder=Path(__file__).parent/'output'
    folder.mkdir(exist_ok=True)
    (folder/'示例策划初稿.md').write_text(report(project,experience,'社区 运营'),encoding='utf-8')
    print('示例已生成：',folder/'示例策划初稿.md')
