#!/usr/bin/env python3
"""
数据分析Agent示例 - 使用LLM Flow Engine的DSL工作流
演示如何使用工作流引擎进行智能数据分析
"""
import asyncio
import sys
import os
import json
import tempfile

# 添加项目根目录到path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_flow_engine.flow_engine import FlowEngine
from llm_flow_engine.functions.file_time import file_write, file_read

class DataAnalysisAgent:
    """数据分析Agent - 使用LLM Flow Engine工作流"""
    
    def __init__(self):
        self.model = "gemma3:4b"
        self.engine = FlowEngine()
        self.temp_dir = tempfile.mkdtemp()
        self.initialized = False
    
    async def initialize(self):
        """初始化数据分析工具"""
        if self.initialized:
            return
            
        print("📊 初始化数据分析Agent（DSL工作流模式）...")
        
        # 注册数据分析专用工具到引擎
        self.engine.register_function("generate_sample_data", self._generate_sample_data)
        self.engine.register_function("load_csv_data", self._load_csv_data)
        self.engine.register_function("create_chart_config", self._create_chart_config)
        self.engine.register_function("analyze_data_statistics", self._analyze_data_statistics)
        
        self.initialized = True
        print("✅ 数据分析Agent（DSL工作流模式）初始化完成")
    
    async def _generate_sample_data(self, data_type: str, size: int = 100) -> str:
        """生成示例数据"""
        import random
        
        if data_type == "sales":
            data = []
            products = ["手机", "电脑", "平板", "耳机", "键盘"]
            regions = ["北京", "上海", "广州", "深圳", "杭州"]
            
            for i in range(size):
                data.append({
                    "id": i + 1,
                    "product": random.choice(products),
                    "region": random.choice(regions),
                    "sales": round(random.uniform(1000, 50000), 2),
                    "quantity": random.randint(1, 100),
                    "date": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
                })
        
        elif data_type == "user":
            data = []
            ages = list(range(18, 65))
            cities = ["北京", "上海", "广州", "深圳", "成都"]
            
            for i in range(size):
                data.append({
                    "user_id": f"U{i+1:04d}",
                    "age": random.choice(ages),
                    "city": random.choice(cities),
                    "login_count": random.randint(1, 365),
                    "spend_amount": round(random.uniform(0, 10000), 2)
                })
        
        else:  # product
            data = []
            categories = ["电子", "服装", "食品", "家居", "运动"]
            
            for i in range(size):
                data.append({
                    "product_id": f"P{i+1:04d}",
                    "category": random.choice(categories),
                    "price": round(random.uniform(10, 5000), 2),
                    "rating": round(random.uniform(1, 5), 1),
                    "review_count": random.randint(0, 1000)
                })
        
        # 保存数据到临时文件
        file_path = os.path.join(self.temp_dir, f"{data_type}_data.json")
        await file_write(file_path, json.dumps(data, ensure_ascii=False, indent=2))
        
        return f"生成{size}条{data_type}示例数据，保存到：{file_path}"
    
    async def _load_csv_data(self, file_path: str) -> str:
        """加载CSV数据"""
        try:
            content = await file_read(file_path)
            lines = content.strip().split('\n')
            return f"成功加载CSV数据，共{len(lines)}行数据。前5行预览：\n" + '\n'.join(lines[:5])
        except Exception as e:
            return f"加载CSV数据失败：{str(e)}"
    
    async def _create_chart_config(self, chart_type: str, data_fields: str) -> str:
        """创建图表配置"""
        config = {
            "type": chart_type,
            "fields": data_fields.split(","),
            "options": {
                "responsive": True,
                "maintainAspectRatio": False
            }
        }
        
        config_path = os.path.join(self.temp_dir, f"{chart_type}_chart_config.json")
        await file_write(config_path, json.dumps(config, indent=2))
        
        return f"图表配置已创建：{config_path}"
    
    async def _analyze_data_statistics(self, data_file: str) -> str:
        """分析数据统计信息"""
        try:
            content = await file_read(data_file)
            data = json.loads(content)
            
            if not data:
                return "数据为空"
            
            # 基本统计
            total_records = len(data)
            
            # 数值字段统计
            numeric_stats = {}
            for item in data:
                for key, value in item.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_stats:
                            numeric_stats[key] = []
                        numeric_stats[key].append(value)
            
            stats_result = {
                "total_records": total_records,
                "numeric_fields": {}
            }
            
            for field, values in numeric_stats.items():
                stats_result["numeric_fields"][field] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": round(sum(values) / len(values), 2),
                    "count": len(values)
                }
            
            return json.dumps(stats_result, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return f"统计分析失败：{str(e)}"
    
    async def analyze_sales_data(self, request: str) -> str:
        """销售数据分析工作流"""
        await self.initialize()
        
        print(f"\n📈 销售数据分析: {request}")
        print("🤖 正在通过工作流进行销售数据分析...")
        
        sales_analysis_dsl = f"""
metadata:
  version: "1.0"
  description: "销售数据分析工作流"

input:
  type: "start"
  name: "analysis_request"
  data:
    request: "{request}"

executors:
  # 步骤1: 生成销售数据
  - name: generate_data
    type: "task"
    func: generate_sample_data
    custom_vars:
      data_type: "sales"
      size: 100

  # 步骤2: 统计分析
  - name: statistical_analysis
    type: "task"
    func: data_statistics
    custom_vars:
      data: "${{generate_data.output}}"
    depends_on: ["generate_data"]

  # 步骤3: 销售趋势分析
  - name: trend_analysis
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于以下销售数据统计结果，分析销售趋势和关键洞察：
        
        用户需求：${{analysis_request.request}}
        数据生成结果：${{generate_data.output}}
        统计分析：${{statistical_analysis.output}}
        
        请提供：
        1. 销售数据总体概况
        2. 关键指标分析（平均销售额、销量等）
        3. 可能的趋势和模式
        4. 业务建议
      model: "{self.model}"
    depends_on: ["statistical_analysis"]

  # 步骤4: 创建可视化配置
  - name: create_visualization
    type: "task"
    func: create_chart_config
    custom_vars:
      chart_type: "bar"
      data_fields: "product,sales,quantity"
    depends_on: ["trend_analysis"]

output:
  name: "analysis_result"
  value: |
    销售数据分析完成：
    ${{trend_analysis.output}}
    
    可视化配置：${{create_visualization.output}}
"""
        
        result = await self.engine.execute_dsl(sales_analysis_dsl, {"request": request})
        
        if result['success']:
            return result['results'].get('analysis_result', '销售分析失败')
        else:
            return f"销售分析错误：{result['error']}"
    
    async def analyze_user_behavior(self, request: str) -> str:
        """用户行为分析工作流"""
        await self.initialize()
        
        print(f"\n👥 用户行为分析: {request}")
        print("🤖 正在通过工作流进行用户行为分析...")
        
        user_analysis_dsl = f"""
metadata:
  version: "1.0"
  description: "用户行为分析工作流"

input:
  type: "start"
  name: "user_request"
  data:
    request: "{request}"

executors:
  # 步骤1: 生成用户数据
  - name: generate_user_data
    type: "task"
    func: generate_sample_data
    custom_vars:
      data_type: "user"
      size: 150

  # 步骤2: 数据过滤和分组
  - name: filter_analysis
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        分析用户数据的关键维度：
        
        用户需求：${{user_request.request}}
        生成的数据：${{generate_user_data.output}}
        
        请分析以下维度：
        1. 用户年龄分布
        2. 城市分布
        3. 活跃度分析（登录次数）
        4. 消费行为分析（消费金额）
        5. 用户价值分段
      model: "{self.model}"
    depends_on: ["generate_user_data"]

  # 步骤3: 深度洞察
  - name: deep_insights
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于用户行为分析结果，提供深度业务洞察：
        
        分析结果：${{filter_analysis.output}}
        
        请提供：
        1. 核心用户特征
        2. 高价值用户画像
        3. 用户留存和活跃度建议
        4. 个性化推荐策略
        5. 运营优化建议
      model: "{self.model}"
    depends_on: ["filter_analysis"]

  # 步骤4: 生成报告
  - name: generate_report
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        将分析结果整合为完整的用户行为分析报告：
        
        基础分析：${{filter_analysis.output}}
        深度洞察：${{deep_insights.output}}
        
        报告格式要求：
        1. 执行摘要
        2. 关键发现
        3. 数据可视化建议
        4. 行动计划
        5. 后续监控指标
      model: "{self.model}"
    depends_on: ["deep_insights"]

output:
  name: "user_analysis_report"
  value: "${{generate_report.output}}"
"""
        
        result = await self.engine.execute_dsl(user_analysis_dsl, {"request": request})
        
        if result['success']:
            return result['results'].get('user_analysis_report', '用户行为分析失败')
        else:
            return f"用户行为分析错误：{result['error']}"
    
    async def comprehensive_data_analysis(self, data_type: str, analysis_goals: str) -> str:
        """综合数据分析工作流 - 多步骤复杂分析"""
        await self.initialize()
        
        print(f"\n🎯 综合数据分析: {data_type} - {analysis_goals}")
        print("🤖 正在执行综合数据分析工作流...")
        
        comprehensive_dsl = f"""
metadata:
  version: "1.0"
  description: "综合数据分析工作流"

input:
  type: "start"
  name: "comprehensive_request"
  data:
    data_type: "{data_type}"
    goals: "{analysis_goals}"

executors:
  # 步骤1: 数据准备
  - name: data_preparation
    type: "task"
    func: generate_sample_data
    custom_vars:
      data_type: "${{comprehensive_request.data_type}}"
      size: 200

  # 步骤2: 数据质量检查
  - name: data_quality_check
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        检查数据质量并提供数据概览：
        
        数据类型：${{comprehensive_request.data_type}}
        数据生成结果：${{data_preparation.output}}
        
        请检查：
        1. 数据完整性
        2. 数据分布情况
        3. 潜在的数据问题
        4. 数据预处理建议
      model: "{self.model}"
    depends_on: ["data_preparation"]

  # 步骤3: 描述性分析
  - name: descriptive_analysis
    type: "task"
    func: data_statistics
    custom_vars:
      data: "${{data_preparation.output}}"
    depends_on: ["data_quality_check"]

  # 步骤4: 探索性分析
  - name: exploratory_analysis
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        进行探索性数据分析：
        
        分析目标：${{comprehensive_request.goals}}
        数据质量：${{data_quality_check.output}}
        描述性统计：${{descriptive_analysis.output}}
        
        探索以下方面：
        1. 数据分布特征
        2. 变量间关系
        3. 异常值识别
        4. 模式发现
        5. 假设生成
      model: "{self.model}"
    depends_on: ["descriptive_analysis"]

  # 步骤5: 高级分析
  - name: advanced_analysis
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于探索性分析结果，进行高级数据分析：
        
        探索性分析：${{exploratory_analysis.output}}
        
        高级分析内容：
        1. 预测性分析建议
        2. 细分分析
        3. 相关性分析
        4. 趋势分析
        5. 业务影响评估
      model: "{self.model}"
    depends_on: ["exploratory_analysis"]

  # 步骤6: 可视化建议
  - name: visualization_recommendations
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于分析结果推荐最佳可视化方案：
        
        高级分析结果：${{advanced_analysis.output}}
        
        推荐内容：
        1. 图表类型选择
        2. 关键指标dashboard设计
        3. 交互式可视化建议
        4. 报告结构设计
        5. 受众定制化建议
      model: "{self.model}"
    depends_on: ["advanced_analysis"]

  # 步骤7: 最终报告
  - name: final_report
    type: "task"
    func: text_merge
    custom_vars:
      texts:
        - "# 综合数据分析报告\n\n## 数据概览\n${{data_quality_check.output}}"
        - "\n\n## 描述性分析\n${{descriptive_analysis.output}}"
        - "\n\n## 探索性分析\n${{exploratory_analysis.output}}"
        - "\n\n## 高级分析\n${{advanced_analysis.output}}"
        - "\n\n## 可视化建议\n${{visualization_recommendations.output}}"
      separator: ""
    depends_on: ["visualization_recommendations"]

output:
  name: "comprehensive_report"
  value: "${{final_report.output}}"
"""
        
        result = await self.engine.execute_dsl(comprehensive_dsl, {"data_type": data_type, "goals": analysis_goals})
        
        if result['success']:
            return result['results'].get('comprehensive_report', '综合分析失败')
        else:
            return f"综合分析错误：{result['error']}"

async def demo_data_analysis_flow():
    """数据分析Agent工作流演示"""
    print("🎨 数据分析Agent演示 (LLM Flow Engine工作流模式)")
    print("=" * 60)
    
    agent = DataAnalysisAgent()
    
    # 测试不同的数据分析工作流
    analysis_scenarios = [
        {
            "type": "销售数据分析",
            "method": "analyze_sales_data",
            "request": "分析销售数据的整体趋势，找出表现最好的产品和地区"
        },
        {
            "type": "用户行为分析", 
            "method": "analyze_user_behavior",
            "request": "分析用户活跃度和消费行为，制定用户增长策略"
        },
        {
            "type": "综合数据分析",
            "method": "comprehensive_data_analysis", 
            "data_type": "product",
            "goals": "产品性能分析和市场定位优化"
        }
    ]
    
    for i, scenario in enumerate(analysis_scenarios, 1):
        print(f"\n📊 分析场景 {i}: {scenario['type']}")
        print("-" * 50)
        
        method = getattr(agent, scenario['method'])
        
        if scenario['type'] == "综合数据分析":
            response = await method(scenario['data_type'], scenario['goals'])
        else:
            response = await method(scenario['request'])
            
        print(f"🤖 分析结果: {response[:500]}...")
        if len(response) > 500:
            print("... (结果已截断)")
        print("=" * 60)
        
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(demo_data_analysis_flow())
