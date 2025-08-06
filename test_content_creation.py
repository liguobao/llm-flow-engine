#!/usr/bin/env python3
"""
测试内容创作Agent的基本功能
"""
import asyncio
import sys
import os

# 添加项目根目录到path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from examples.content_creation_agent_flow import ContentCreationAgent

async def test_agent_initialization():
    """测试Agent初始化"""
    print("🔧 测试Agent初始化...")
    
    try:
        agent = ContentCreationAgent()
        await agent.initialize()
        print("✅ Agent初始化成功")
        return True
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_blog_creation():
    """测试简单的博客创作功能"""
    print("\n📝 测试博客创作功能...")
    
    try:
        agent = ContentCreationAgent()
        
        # 创建一个非常简单的测试
        simple_topic = "Python基础教程"
        response = await agent.create_blog_article(simple_topic, "technical")
        
        # 处理ExecutorResult类型
        if hasattr(response, 'output') or hasattr(response, 'value'):
            # 如果是ExecutorResult类型，获取输出内容
            content = getattr(response, 'output', None) or getattr(response, 'value', str(response))
        else:
            content = str(response)
        
        if content and "Python" in content:
            print("✅ 博客创作功能正常")
            print(f"创作结果预览: {content[:200]}...")
            return True
        else:
            print(f"❌ 博客创作功能异常: {content}")
            return False
            
    except Exception as e:
        print(f"❌ 博客创作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🎯 内容创作Agent功能测试")
    print("=" * 50)
    
    # 测试基本功能
    tests = [
        ("初始化测试", test_agent_initialization),
        ("博客创作测试", test_simple_blog_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 开始 {test_name}")
        result = await test_func()
        results.append((test_name, result))
        print(f"{'✅ 通过' if result else '❌ 失败'}: {test_name}")
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {test_name}")
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过！内容创作Agent运行正常")
    else:
        print("⚠️ 部分测试失败，需要检查相关功能")

if __name__ == "__main__":
    asyncio.run(main())
