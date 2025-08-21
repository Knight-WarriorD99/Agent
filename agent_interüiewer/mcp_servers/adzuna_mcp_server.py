#!/usr/bin/env python3
"""
Adzuna API MCP 服务器
提供市场薪资数据查询功能
"""

import asyncio
import json
import aiohttp
from typing import Optional, Dict, Any
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Adzuna API 配置（从环境变量读取，避免明文）
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
ADZUNA_BASE_URL = os.getenv("ADZUNA_BASE_URL", "https://api.adzuna.com/v1/api/jobs/gb/search/1")

class AdzunaMCPServer:
    def __init__(self):
        self.server = Server("adzuna-api", version="1.0.0")
        self.setup_tools()
    
    def setup_tools(self):
        """设置 MCP 工具"""
        
        @self.server.call_tool()
        async def get_market_salary_data(
            position: str = "Python Developer",
            location: str = "London",
            results_per_page: int = 50
        ) -> Dict[str, Any]:
            """
            获取指定职位和地点的市场薪资数据
            
            Args:
                position: 职位名称
                location: 地点
                results_per_page: 返回结果数量
            
            Returns:
                包含市场薪资数据的字典
            """
            try:
                # 构建 API 参数
                params = {
                    'app_id': ADZUNA_APP_ID,
                    'app_key': ADZUNA_APP_KEY,
                    'results_per_page': results_per_page,
                    'what': position,
                    'where': location
                }
                
                # 调用 Adzuna API
                async with aiohttp.ClientSession() as session:
                    async with session.get(ADZUNA_BASE_URL, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self.analyze_salary_data(data)
                        else:
                            return {
                                "error": f"API 请求失败: {response.status}",
                                "success": False
                            }
            except Exception as e:
                return {
                    "error": f"获取市场薪资数据失败: {str(e)}",
                    "success": False
                }
        
        @self.server.call_tool()
        async def get_salary_statistics(
            position: str = "Python Developer",
            location: str = "London"
        ) -> Dict[str, Any]:
            """
            获取薪资统计信息
            
            Args:
                position: 职位名称
                location: 地点
            
            Returns:
                薪资统计信息
            """
            result = await get_market_salary_data(position, location)
            if result.get("success", True):
                return {
                    "position": position,
                    "location": location,
                    "average_salary": result.get("average_salary"),
                    "min_salary": result.get("min_salary"),
                    "max_salary": result.get("max_salary"),
                    "sample_count": result.get("sample_count"),
                    "currency": result.get("currency", "GBP")
                }
            else:
                return result
    
    def analyze_salary_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析 API 返回的薪资数据"""
        try:
            results = api_data.get('results', [])
            if not results:
                return {
                    "error": "未找到相关职位数据",
                    "success": False
                }
                
            salaries = []
            for job in results:
                salary_min = job.get('salary_min')
                salary_max = job.get('salary_max')
                if salary_min and salary_max:
                    avg_salary = (salary_min + salary_max) / 2
                    salaries.append(avg_salary)
            
            if salaries:
                avg_market_salary = sum(salaries) / len(salaries)
                min_salary = min(salaries)
                max_salary = max(salaries)
                
                return {
                    'average_salary': round(avg_market_salary, 2),
                    'min_salary': round(min_salary, 2),
                    'max_salary': round(max_salary, 2),
                    'sample_count': len(salaries),
                    'currency': 'GBP',
                    'success': True
                }
            else:
                return {
                    "error": "未找到有效的薪资数据",
                    "success": False
                }
        except Exception as e:
            return {
                "error": f"分析薪资数据失败: {str(e)}",
                "success": False
            }

async def main():
    """启动 MCP 服务器"""
    server = AdzunaMCPServer()
    
    # 创建 stdio 服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="adzuna-api",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
