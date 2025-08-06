#!/usr/bin/env python3
"""
内容创作Agent示例 - 使用LLM Flow Engine的DSL工作流
演示如何使用工作流引擎进行智能内容创作
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
from llm_flow_engine.functions.knowledge_base import knowledge_base_create, knowledge_base_add_document

class ContentCreationAgent:
    """内容创作Agent - 使用LLM Flow Engine工作流"""
    
    def __init__(self):
        self.model = "gemma3:1b"
        self.kb_name = "content_writing_kb"
        self.engine = FlowEngine()
        self.temp_dir = tempfile.mkdtemp()
        self.initialized = False
    
    async def initialize(self):
        """初始化内容创作工具和知识库"""
        if self.initialized:
            return
            
        print("✍️ 初始化内容创作Agent（DSL工作流模式）...")
        
        # 创建写作素材知识库
        await knowledge_base_create(self.kb_name, "内容创作知识库 - 包含写作模板和素材")
        
        # 添加写作模板和素材
        templates = [
            {
                "title": "技术博客模板",
                "content": """
# {标题}

## 概述
简要介绍技术主题和解决的问题。

## 背景
详细说明问题背景和现状。

## 解决方案
### 方案1: {方案名称}
具体实现步骤和代码示例。

### 方案2: {备选方案}
alternative solution

## 实践案例
实际应用示例和结果分析。

## 总结
总结要点和后续优化方向。
                """
            },
            {
                "title": "产品介绍模板",
                "content": """
## 产品概述
产品的核心功能和价值主张。

## 主要特性
- 特性1：详细说明
- 特性2：使用场景
- 特性3：技术优势

## 使用场景
具体的应用场景和目标用户。

## 技术架构
系统架构图和技术栈说明。

## 快速开始
安装和使用步骤。
                """
            },
            {
                "title": "营销文案模板",
                "content": """
【吸引注意】震撼标题

【激发兴趣】产品亮点
- 解决核心痛点
- 独特价值主张
- 用户成功案例

【建立渴望】使用效果
具体的量化结果和用户反馈

【促成行动】立即体验
明确的行动指引和联系方式
                """
            }
        ]
        
        for template in templates:
            await knowledge_base_add_document(
                self.kb_name, 
                template["title"], 
                template["content"], 
                {"type": "template", "title": template["title"]}
            )
        
        # 注册内容创作专用工具到引擎
        self.engine.register_function("save_content", self._save_content)
        self.engine.register_function("optimize_for_seo", self._optimize_for_seo)
        self.engine.register_function("create_social_variants", self._create_social_variants)
        self.engine.register_function("text_merge", self._text_merge)
        
        self.initialized = True
        print("✅ 内容创作Agent（DSL工作流模式）初始化完成")
    
    async def _save_content(self, content: str = None, filename: str = None, **kwargs) -> str:
        """保存内容到文件"""
        # 从kwargs中获取参数（如果没有通过位置参数传递）
        if content is None:
            content = kwargs.get('content', '')
        if filename is None:
            filename = kwargs.get('filename', 'untitled.md')
            
        file_path = os.path.join(self.temp_dir, filename)
        await file_write(file_path, content)
        return f"内容已保存到：{file_path}"
    
    async def _optimize_for_seo(self, content: str, keywords: str) -> str:
        """SEO优化内容"""
        # 这里可以实现SEO优化逻辑
        return f"SEO优化完成，关键词：{keywords}\n优化后的内容：{content[:200]}..."
    
    async def _create_social_variants(self, content: str, platforms: str) -> str:
        """创建社交媒体变体"""
        platform_list = platforms.split(",")
        variants = {}
        for platform in platform_list:
            variants[platform.strip()] = f"{platform.strip()}版本：{content[:100]}..."
        return json.dumps(variants, ensure_ascii=False, indent=2)
    
    def _text_merge(self, separator: str = "
", **kwargs):
        """合并多个文本片段"""
        try:
            texts = kwargs.get('texts', [])
            result = separator.join(texts)
            return result
        except Exception as e:
            raise ValueError(f"文本合并失败: {e}")
    
    async def create_blog_article(self, topic: str, article_type: str = "technical") -> str:
        """创建博客文章的完整工作流"""
        await self.initialize()
        
        print(f"\n📝 博客文章创作: {topic} ({article_type})")
        print("🤖 正在通过工作流进行博客创作...")
        
        blog_creation_dsl = f"""
metadata:
  version: "1.0"
  description: "博客文章创作工作流"

input:
  type: "start"
  name: "blog_request"
  data:
    topic: "{topic}"
    type: "{article_type}"

executors:
  # 步骤1: 查找相关模板
  - name: find_template
    type: "task"
    func: knowledge_base_search
    custom_vars:
      kb_name: "{self.kb_name}"
      query: "${{blog_request.type}} 模板"
      top_k: 1

  # 步骤2: 生成文章大纲
  - name: create_outline
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于以下模板和主题，生成详细的博客文章大纲：
        
        主题：${{blog_request.topic}}
        类型：${{blog_request.type}}
        参考模板：${{find_template.output}}
        
        要求：
        1. 结构清晰的多级大纲
        2. 每个部分的关键点
        3. 预估字数和阅读时间
        4. 目标读者群体
      model: "{self.model}"
    depends_on: ["find_template"]

  # 步骤3: 扩展引言部分
  - name: write_introduction
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于大纲写作引言部分：
        
        文章主题：${{blog_request.topic}}
        文章大纲：${{create_outline.output}}
        
        引言要求：
        1. 吸引读者注意力
        2. 明确文章价值主张
        3. 概述文章结构
        4. 字数控制在200-300字
      model: "{self.model}"
    depends_on: ["create_outline"]

  # 步骤4: 扩展主体内容
  - name: write_main_content
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于大纲扩展主体内容：
        
        文章大纲：${{create_outline.output}}
        引言部分：${{write_introduction.output}}
        
        主体内容要求：
        1. 逻辑清晰，层次分明
        2. 包含具体案例和示例
        3. 技术内容要准确详细
        4. 字数控制在800-1200字
      model: "{self.model}"
    depends_on: ["write_introduction"]

  # 步骤5: 写作结论
  - name: write_conclusion
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        为文章写作结论部分：
        
        引言：${{write_introduction.output}}
        主体内容：${{write_main_content.output}}
        
        结论要求：
        1. 总结关键要点
        2. 提供行动建议
        3. 展望未来发展
        4. 字数控制在150-200字
      model: "{self.model}"
    depends_on: ["write_main_content"]

  # 步骤6: 合并完整文章
  - name: merge_article
    type: "task"
    func: text_merge
    custom_vars:
      texts:
        - "# ${{blog_request.topic}}\n\n"
        - "${{write_introduction.output}}\n\n"
        - "${{write_main_content.output}}\n\n"
        - "## 总结\n\n${{write_conclusion.output}}"
      separator: ""
    depends_on: ["write_conclusion"]

  # 步骤7: 内容优化
  - name: optimize_content
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        优化以下文章的可读性和SEO：
        
        文章内容：${{merge_article.output}}
        
        优化要求：
        1. 改善句子结构和段落组织
        2. 添加关键词（但不过度优化）
        3. 确保语言流畅自然
        4. 添加小标题和格式化
      model: "{self.model}"
    depends_on: ["merge_article"]

  # 步骤8: 保存文章
  - name: save_article
    type: "task"
    func: save_content
    custom_vars:
      content: "${{optimize_content.output}}"
      filename: "blog_${{blog_request.topic}}.md"
    depends_on: ["optimize_content"]

output:
  name: "blog_article"
  value: |
    博客文章创作完成！
    
    文章标题：${{blog_request.topic}}
    文章类型：${{blog_request.type}}
    保存位置：${{save_article.output}}
    
    文章内容：
    ${{optimize_content.output}}
"""
        
        result = await self.engine.execute_dsl(blog_creation_dsl, {"topic": topic, "type": article_type})
        
        if result['success']:
            return result['results'].get('blog_article', '博客创作失败')
        else:
            return f"博客创作错误：{result['error']}"
    
    async def create_marketing_content(self, product: str, target_audience: str) -> str:
        """创建营销内容的完整工作流"""
        await self.initialize()
        
        print(f"\n🎯 营销内容创作: {product} -> {target_audience}")
        print("🤖 正在通过工作流创作营销内容...")
        
        marketing_dsl = f"""
metadata:
  version: "1.0"
  description: "营销内容创作工作流"

input:
  type: "start"
  name: "marketing_request"
  data:
    product: "{product}"
    audience: "{target_audience}"

executors:
  # 步骤1: 获取营销模板
  - name: get_marketing_template
    type: "task"
    func: knowledge_base_search
    custom_vars:
      kb_name: "{self.kb_name}"
      query: "营销文案模板"
      top_k: 1

  # 步骤2: 分析目标受众
  - name: analyze_audience
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        分析目标受众特征和需求：
        
        产品：${{marketing_request.product}}
        目标受众：${{marketing_request.audience}}
        
        分析内容：
        1. 受众画像（年龄、职业、兴趣）
        2. 核心需求和痛点
        3. 消费习惯和偏好
        4. 沟通语调建议
        5. 渠道偏好
      model: "{self.model}"

  # 步骤3: 产品卖点提炼
  - name: extract_selling_points
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        提炼产品核心卖点：
        
        产品：${{marketing_request.product}}
        受众分析：${{analyze_audience.output}}
        
        提炼内容：
        1. 核心功能特性
        2. 独特价值主张
        3. 竞争优势
        4. 用户收益点
        5. 情感连接点
      model: "{self.model}"
    depends_on: ["analyze_audience"]

  # 步骤4: 创作主标题
  - name: create_headlines
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于产品卖点创作吸引人的标题：
        
        产品卖点：${{extract_selling_points.output}}
        目标受众：${{analyze_audience.output}}
        
        创作要求：
        1. 5个不同风格的标题
        2. 突出核心价值
        3. 激发好奇心或紧迫感
        4. 符合目标受众语言习惯
      model: "{self.model}"
    depends_on: ["extract_selling_points"]

  # 步骤5: 撰写营销正文
  - name: write_marketing_copy
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于模板和分析结果撰写营销文案：
        
        营销模板：${{get_marketing_template.output}}
        标题选项：${{create_headlines.output}}
        产品卖点：${{extract_selling_points.output}}
        受众分析：${{analyze_audience.output}}
        
        文案要求：
        1. 遵循AIDA结构（注意-兴趣-渴望-行动）
        2. 突出产品独特价值
        3. 包含社会证明元素
        4. 明确的行动召唤
        5. 字数控制在300-500字
      model: "{self.model}"
    depends_on: ["create_headlines"]

  # 步骤6: 创建多平台版本
  - name: create_platform_versions
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        将营销文案改写为不同平台版本：
        
        原始文案：${{write_marketing_copy.output}}
        
        平台要求：
        1. 微信朋友圈版本（简洁有趣）
        2. 微博版本（话题性强）
        3. 小红书版本（种草风格）
        4. LinkedIn版本（专业严谨）
        5. 短视频脚本版本
      model: "{self.model}"
    depends_on: ["write_marketing_copy"]

  # 步骤7: A/B测试版本
  - name: create_ab_variants
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        创建A/B测试版本：
        
        主版本：${{write_marketing_copy.output}}
        
        变体要求：
        1. 版本A：强调功能特性
        2. 版本B：强调情感价值
        3. 版本C：强调价格优势
        4. 每个版本都要有不同的行动召唤
      model: "{self.model}"
    depends_on: ["write_marketing_copy"]

  # 步骤8: 合并最终结果
  - name: compile_final_content
    type: "task"
    func: text_merge
    custom_vars:
      texts:
        - "# 营销内容创作结果\n\n"
        - "## 产品：${{marketing_request.product}}\n"
        - "## 目标受众：${{marketing_request.audience}}\n\n"
        - "## 主要营销文案\n${{write_marketing_copy.output}}\n\n"
        - "## 多平台版本\n${{create_platform_versions.output}}\n\n"
        - "## A/B测试版本\n${{create_ab_variants.output}}"
      separator: ""
    depends_on: ["create_platform_versions", "create_ab_variants"]

output:
  name: "marketing_content"
  value: "${{compile_final_content.output}}"
"""
        
        result = await self.engine.execute_dsl(marketing_dsl, {"product": product, "audience": target_audience})
        
        if result['success']:
            return result['results'].get('marketing_content', '营销内容创作失败')
        else:
            return f"营销内容创作错误：{result['error']}"
    
    async def create_content_series(self, theme: str, content_count: int = 3) -> str:
        """创建系列内容的工作流"""
        await self.initialize()
        
        print(f"\n📚 系列内容创作: {theme} ({content_count}篇)")
        print("🤖 正在通过工作流创作系列内容...")
        
        series_dsl = f"""
metadata:
  version: "1.0"
  description: "系列内容创作工作流"

input:
  type: "start"
  name: "series_request"
  data:
    theme: "{theme}"
    count: {content_count}

executors:
  # 步骤1: 规划系列结构
  - name: plan_series_structure
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        为以下主题规划系列内容结构：
        
        主题：${{series_request.theme}}
        文章数量：${{series_request.count}}
        
        规划要求：
        1. 系列总体介绍
        2. 每篇文章的主题和重点
        3. 文章间的逻辑关系
        4. 难度递进安排
        5. 目标读者群体
      model: "{self.model}"

  # 步骤2: 创作第一篇（基础篇）
  - name: create_article_1
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        基于系列规划创作第一篇文章：
        
        系列规划：${{plan_series_structure.output}}
        
        第一篇要求：
        1. 作为系列开篇，介绍整个主题
        2. 建立读者兴趣和期待
        3. 提供基础知识铺垫
        4. 字数控制在800-1000字
        5. 预告后续内容
      model: "{self.model}"
    depends_on: ["plan_series_structure"]

  # 步骤3: 创作第二篇（进阶篇）
  - name: create_article_2
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        创作系列第二篇文章：
        
        系列规划：${{plan_series_structure.output}}
        第一篇内容：${{create_article_1.output}}
        
        第二篇要求：
        1. 承接第一篇的内容
        2. 深入探讨核心概念
        3. 提供实践案例
        4. 字数控制在1000-1200字
        5. 引导到第三篇
      model: "{self.model}"
    depends_on: ["create_article_1"]

  # 步骤4: 创作第三篇（实战篇）
  - name: create_article_3
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        创作系列第三篇文章：
        
        系列规划：${{plan_series_structure.output}}
        前两篇内容总结：
        第一篇：${{create_article_1.output}}
        第二篇：${{create_article_2.output}}
        
        第三篇要求：
        1. 提供具体实施方案
        2. 包含详细步骤说明
        3. 分享最佳实践
        4. 总结整个系列
        5. 字数控制在1200-1500字
      model: "{self.model}"
    depends_on: ["create_article_2"]
    condition: "${{series_request.count >= 3}}"

  # 步骤5: 创建系列索引
  - name: create_series_index
    type: "task"
    func: llm_simple_call
    custom_vars:
      user_input: |
        为系列内容创建索引页面：
        
        系列主题：${{series_request.theme}}
        系列规划：${{plan_series_structure.output}}
        
        索引要求：
        1. 系列总体介绍
        2. 每篇文章简介和链接
        3. 阅读建议和顺序
        4. 适合的读者群体
        5. 学习目标和收获
      model: "{self.model}"
    depends_on: ["create_article_3"]

  # 步骤6: 合并系列内容
  - name: compile_series
    type: "task"
    func: text_merge
    custom_vars:
      texts:
        - "# ${{series_request.theme}} 系列内容\n\n"
        - "## 系列索引\n${{create_series_index.output}}\n\n"
        - "## 第一篇：基础篇\n${{create_article_1.output}}\n\n"
        - "## 第二篇：进阶篇\n${{create_article_2.output}}\n\n"
        - "## 第三篇：实战篇\n${{create_article_3.output}}"
      separator: ""
    depends_on: ["create_series_index"]

output:
  name: "content_series"
  value: "${{compile_series.output}}"
"""
        
        result = await self.engine.execute_dsl(series_dsl, {"theme": theme, "count": content_count})
        
        if result['success']:
            return result['results'].get('content_series', '系列内容创作失败')
        else:
            return f"系列内容创作错误：{result['error']}"

async def demo_content_creation_flow():
    """内容创作Agent工作流演示"""
    print("🎨 内容创作Agent演示 (LLM Flow Engine工作流模式)")
    print("=" * 60)
    
    agent = ContentCreationAgent()
    
    # 测试不同的内容创作工作流
    creation_scenarios = [
        {
            "type": "技术博客",
            "method": "create_blog_article",
            "topic": "Python异步编程最佳实践",
            "article_type": "technical"
        },
        {
            "type": "营销内容",
            "method": "create_marketing_content", 
            "product": "AI代码助手",
            "target_audience": "Python开发者"
        },
        {
            "type": "系列内容",
            "method": "create_content_series",
            "theme": "机器学习入门到实战",
            "content_count": 3
        }
    ]
    
    for i, scenario in enumerate(creation_scenarios, 1):
        print(f"\n✍️ 创作场景 {i}: {scenario['type']}")
        print("-" * 50)
        
        method = getattr(agent, scenario['method'])
        
        if scenario['type'] == "技术博客":
            response = await method(scenario['topic'], scenario['article_type'])
        elif scenario['type'] == "营销内容":
            response = await method(scenario['product'], scenario['target_audience'])
        elif scenario['type'] == "系列内容":
            response = await method(scenario['theme'], scenario['content_count'])
            
        print(f"🎨 创作结果: {response[:600]}...")
        if len(response) > 600:
            print("... (结果已截断)")
        print("=" * 60)
        
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(demo_content_creation_flow())
