#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
任务列表生成器模块

该模块提供了分析用户问题并生成结构化to do list的功能，
包括问题分析、任务提取、优先级排序和列表格式化等核心功能。
"""

import re
import logging
from typing import List, Dict, Tuple, Optional

# 配置日志 - 优化性能和可靠性
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 捕获并记录未处理的异常
def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("未处理的异常:", exc_info=(exc_type, exc_value, exc_traceback))

import sys
sys.excepthook = handle_uncaught_exception


class TodoListGenerator:
    """
    任务列表生成器类
    
    负责分析用户问题，提取任务项，设置优先级，并生成结构化的to do list。
    """
    
    def __init__(self):
        """初始化任务列表生成器，预编译正则表达式以提高性能"""
        # 定义常见的任务关键词和模式
        self.task_keywords = {
            '分析': ['分析', '研究', '评估', '审查', '检查', '调研', '考察'],
            '设计': ['设计', '规划', '架构', '布局', '蓝图', '策划'],
            '实现': ['实现', '开发', '编写', '创建', '构建', '开发', '制作'],
            '测试': ['测试', '验证', '调试', '检查', '确认', '检验'],
            '文档': ['文档', '记录', '说明', '注释', '报告'],
            '优化': ['优化', '改进', '提升', '增强', '完善'],
            '修复': ['修复', '修复bug', '解决', '处理', '更正', '排除']
        }
        
        # 预编译常用正则表达式，提高性能
        self.theme_patterns_regex = [
            re.compile(r'开发(.*?)功能'),
            re.compile(r'实现(.*?)模块'),
            re.compile(r'创建(.*?)系统'),
            re.compile(r'优化(.*?)性能'),
            re.compile(r'解决(.*?)问题')
        ]
        
        # 预编译分隔符正则表达式
        self.delimiter_pattern = re.compile(r'[、,]')
        self.connector_pattern = re.compile(r'和')
        self.punctuation_pattern = re.compile(r'[。，、；："\']')
        self.end_punctuation_pattern = re.compile(r'[，。！？；：]')
        
        # 优先级关键词
        self.priority_keywords = {
            'high': ['必须', '重要', '紧急', '关键', '核心'],
            'medium': ['需要', '建议', '一般', '常规'],
            'low': ['可以', '可选', '次要', '后续']
        }
        
        # 任务依赖模式
        self.dependency_patterns = {
            '前置': ['首先', '第一步', '需要先', '在...之前'],
            '后置': ['然后', '接着', '之后', '下一步', '最后']
        }
    
    def analyze_question(self, question: str) -> Dict[str, any]:
        """
        分析用户问题，提取关键信息
        
        Args:
            question: 用户输入的问题字符串
            
        Returns:
            包含问题分析结果的字典
        """
        logger.info(f"分析问题: {question}")
        
        analysis_result = {
            'original_question': question,
            'main_theme': self._extract_main_theme(question),
            'key_actions': self._extract_key_actions(question),
            'priority_indicators': self._extract_priority_indicators(question),
            'dependencies': self._identify_dependencies(question)
        }
        
        logger.info(f"问题分析结果: {analysis_result}")
        return analysis_result
    
    def extract_tasks(self, analysis_result: Dict[str, any]) -> List[Dict[str, str]]:
        """
        从问题分析结果中提取任务列表
        
        Args:
            analysis_result: 问题分析结果字典
            
        Returns:
            任务字典列表，每个字典包含任务描述和初始优先级
        """
        tasks = []
        question = analysis_result['original_question']
        
        # 1. 提取并列任务（这是最优先的，尤其是包含标记后的并列内容）
        parallel_tasks = self._extract_parallel_tasks(question)
        
        if parallel_tasks and len(parallel_tasks) > 1:
            # 如果有多个并列任务，则分别处理
            for task_desc in parallel_tasks:
                # 从每个并列任务中提取核心内容
                task_content = self._clean_task_description(task_desc)
                if task_content and not self._is_duplicate_task(task_content, tasks):
                    # 使用相同的优先级规则
                    initial_priority = self._determine_initial_priority(analysis_result['priority_indicators'])
                    tasks.append({
                        'content': task_content,
                        'priority': initial_priority,
                        'status': 'pending',
                        'id': str(len(tasks) + 1)
                    })
        else:
            # 2. 如果没有并列任务或只有一个，则基于关键词提取任务
            key_actions = analysis_result['key_actions']
            for action_type, keywords in self.task_keywords.items():
                for keyword in keywords:
                    if keyword in question:
                        task_description = self._generate_task_description(question, keyword, action_type)
                        if task_description and not self._is_duplicate_task(task_description, tasks):
                            tasks.append({
                                'content': task_description,
                                'priority': 'medium',  # 默认优先级
                                'status': 'pending',
                                'id': str(len(tasks) + 1)
                            })
        
        # 3. 如果没有提取到足够的任务，尝试提取子任务
        if len(tasks) < 1:
            sub_tasks = self._extract_subtasks(question)
            for subtask in sub_tasks:
                # 子任务默认使用中等优先级
                task_content = self._clean_task_description(subtask)
                if task_content and not self._is_duplicate_task(task_content, tasks):
                    tasks.append({
                        'content': task_content,
                        'priority': 'medium',
                        'status': 'pending',
                        'id': str(len(tasks) + 1)
                    })
        
        # 4. 如果没有通过关键词提取到任务，则创建默认任务
        if not tasks:
            default_task = self._generate_default_tasks(question)
            tasks.extend(default_task)
        
        logger.info(f"提取的原始任务列表: {tasks}")
        return tasks
    
    def prioritize_tasks(self, tasks: List[Dict[str, str]], analysis_result: Dict[str, any]) -> List[Dict[str, str]]:
        """
        为任务列表设置优先级
        
        Args:
            tasks: 任务列表
            analysis_result: 问题分析结果
            
        Returns:
            更新优先级后的任务列表
        """
        prioritized_tasks = tasks.copy()
        priority_indicators = analysis_result['priority_indicators']
        dependencies = analysis_result['dependencies']
        question = analysis_result['original_question']
        
        # 计算每个任务的优先级分数
        task_scores = {}
        for i, task in enumerate(prioritized_tasks):
            task_text = task['content']
            score = self._calculate_priority_score(task_text, priority_indicators, question)
            task_scores[i] = score
        
        # 根据分数调整优先级
        for i, task in enumerate(prioritized_tasks):
            score = task_scores[i]
            if score >= 8:
                task['priority'] = 'high'
            elif score <= 3:
                task['priority'] = 'low'
            else:
                task['priority'] = 'medium'
        
        # 根据依赖关系排序任务
        if dependencies:
            prioritized_tasks = self._sort_by_dependencies(prioritized_tasks, dependencies)
        else:
            # 没有明显依赖时，按任务类型和优先级排序
            prioritized_tasks = self._sort_by_task_type_and_priority(prioritized_tasks)
        
        # 重新分配ID以反映排序
        for idx, task in enumerate(prioritized_tasks):
            task['id'] = str(idx + 1)
        
        logger.info(f"优先级排序后的任务列表: {prioritized_tasks}")
        return prioritized_tasks
    
    def _calculate_priority_score(self, task_text: str, priority_indicators: List[str], question: str) -> int:
        """
        计算任务的优先级分数
        
        Args:
            task_text: 任务描述文本
            priority_indicators: 问题中的优先级指示词
            question: 原始问题文本
            
        Returns:
            优先级分数(0-10)
        """
        score = 5  # 基础分数
        
        # 高优先级关键词增加分数
        high_keywords = self.priority_keywords['high']
        for keyword in high_keywords:
            if keyword in task_text or keyword in priority_indicators:
                score += 3
        
        # 低优先级关键词减少分数
        low_keywords = self.priority_keywords['low']
        for keyword in low_keywords:
            if keyword in task_text or keyword in priority_indicators:
                score -= 2
        
        # 特殊任务类型的优先级调整
        urgent_tasks = ['修复', '解决', '处理', '排除']
        for urgent_task in urgent_tasks:
            if urgent_task in task_text:
                score += 2
        
        # 时间相关关键词调整
        time_keywords = {
            '今天': 2,
            '立即': 3,
            '马上': 3,
            '尽快': 2,
            '稍后': -2,
            '后续': -3
        }
        for keyword, time_score in time_keywords.items():
            if keyword in task_text or keyword in question:
                score += time_score
        
        # 确保分数在0-10范围内
        return max(0, min(10, score))
    
    def _sort_by_task_type_and_priority(self, tasks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        根据任务类型和优先级进行排序
        
        Args:
            tasks: 任务列表
            
        Returns:
            排序后的任务列表
        """
        # 优先级权重
        priority_weights = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        # 定义任务类型的优先级顺序
        action_order = {
            '分析': 0,
            '设计': 1,
            '实现': 2,
            '修复': 2,  # 修复与实现优先级相同
            '测试': 3,
            '优化': 4,
            '文档': 5
        }
        
        # 排序函数
        def task_sort_key(task):
            content = task['content']
            priority = task['priority']
            
            # 确定任务类型顺序
            task_order = len(action_order)
            for action, order in action_order.items():
                if action in content:
                    task_order = order
                    break
            
            # 复合排序键：(任务类型顺序, 优先级权重)
            # 注意：优先级越高，权重越大，所以加负号使其排在前面
            return (task_order, -priority_weights.get(priority, 2))
        
        return sorted(tasks, key=task_sort_key)
    
    def format_todo_list(self, tasks: List[Dict[str, str]], format_type: str = 'json', title: str = None) -> str:
        """
        格式化任务列表为指定格式
        
        Args:
            tasks: 任务列表
            format_type: 输出格式类型，支持 'json', 'text', 'markdown', 'simple', 'html'
            title: 可选的任务列表标题
            
        Returns:
            格式化后的任务列表字符串
        """
        # 使用默认标题或自定义标题
        default_title = "任务列表"
        list_title = title if title else default_title
        
        if format_type == 'json':
            import json
            return json.dumps({'title': list_title, 'todos': tasks}, ensure_ascii=False, indent=2)
        
        elif format_type == 'text':
            result = f"{list_title}:\n"
            result += "=" * (len(list_title) + 2) + "\n\n"
            
            # 按优先级分组输出
            high_priority = [t for t in tasks if t['priority'] == 'high']
            medium_priority = [t for t in tasks if t['priority'] == 'medium']
            low_priority = [t for t in tasks if t['priority'] == 'low']
            
            if high_priority:
                result += "【高优先级任务】\n"
                for task in high_priority:
                    result += f"{task['id']}. [紧急] {task['content']}\n"
                result += "\n"
            
            if medium_priority:
                result += "【中优先级任务】\n"
                for task in medium_priority:
                    result += f"{task['id']}. [普通] {task['content']}\n"
                result += "\n"
            
            if low_priority:
                result += "【低优先级任务】\n"
                for task in low_priority:
                    result += f"{task['id']}. [可选] {task['content']}\n"
            
            return result
        
        elif format_type == 'markdown':
            result = f"# {list_title}\n\n"
            
            # 任务统计信息
            total_tasks = len(tasks)
            high_count = sum(1 for t in tasks if t['priority'] == 'high')
            medium_count = sum(1 for t in tasks if t['priority'] == 'medium')
            low_count = sum(1 for t in tasks if t['priority'] == 'low')
            
            result += f"**任务统计**: 共 {total_tasks} 项任务（高优先级: {high_count}, 中优先级: {medium_count}, 低优先级: {low_count}）\n\n"
            
            # 表格形式的任务列表
            result += "## 任务详情\n\n"
            result += "| ID | 优先级 | 状态 | 任务描述 |\n"
            result += "|----|--------|------|----------|\n"
            
            # 优先级颜色标记
            priority_colors = {
                'high': '🔴',
                'medium': '🟡', 
                'low': '🔵'
            }
            
            status_emojis = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅'
            }
            
            for task in tasks:
                priority_text = {'high': '高', 'medium': '中', 'low': '低'}.get(task['priority'], '中')
                status_text = {'pending': '待处理', 'in_progress': '进行中', 'completed': '已完成'}.get(task['status'], '待处理')
                priority_color = priority_colors.get(task['priority'], '⚪')
                status_emoji = status_emojis.get(task['status'], '➖')
                
                result += f"| {task['id']} | {priority_color} {priority_text} | {status_emoji} {status_text} | {task['content']} |\n"
            
            return result
        
        elif format_type == 'simple':
            """简洁格式，适合纯文本显示"""
            result = f"{list_title}\n"
            result += "-" * (len(list_title)) + "\n"
            
            for task in tasks:
                priority_marker = {'high': '!', 'medium': '-', 'low': ' '}.get(task['priority'], '-')
                result += f"[{priority_marker}] {task['content']}\n"
            
            return result
        
        elif format_type == 'html':
            """HTML格式输出，适合在网页中显示"""
            result = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{list_title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .task-container {{
            margin-top: 20px;
        }}
        .task-item {{
            padding: 10px 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            background-color: #f9f9f9;
        }}
        .task-high {{
            border-left-color: #e74c3c;
            background-color: #ffeaea;
        }}
        .task-medium {{
            border-left-color: #f39c12;
            background-color: #fff8e1;
        }}
        .task-low {{
            border-left-color: #27ae60;
            background-color: #e8f5e9;
        }}
        .task-id {{
            font-weight: bold;
            margin-right: 10px;
        }}
        .task-priority {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 10px;
        }}
        .priority-high {{
            background-color: #e74c3c;
            color: white;
        }}
        .priority-medium {{
            background-color: #f39c12;
            color: white;
        }}
        .priority-low {{
            background-color: #27ae60;
            color: white;
        }}
        .task-content {{
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <h1>{list_title}</h1>
    <div class="task-container">
"""
            
            for task in tasks:
                priority_class = f"task-{task['priority']}"
                priority_label_class = f"priority-{task['priority']}"
                priority_text = {'high': '高优先级', 'medium': '中优先级', 'low': '低优先级'}.get(task['priority'], '中优先级')
                
                result += f"""        <div class="task-item {priority_class}">
            <span class="task-id">{task['id']}.</span>
            <span class="task-priority {priority_label_class}">{priority_text}</span>
            <div class="task-content">{task['content']}</div>
        </div>
"""
            
            result += """
    </div>
</body>
</html>
"""
            return result
        
        else:
            supported_formats = ['json', 'text', 'markdown', 'simple', 'html']
            raise ValueError(f"不支持的格式类型: {format_type}。支持的格式有: {', '.join(supported_formats)}")
            
    def generate_todo_list(self, question: str, format_type: str = 'json', title: str = None) -> str:
        """
        生成完整的to do list的主函数
        
        Args:
            question: 用户输入的问题
            format_type: 输出格式
            title: 可选的任务列表标题
            
        Returns:
            格式化的任务列表
        """
        # 分析问题
        analysis_result = self.analyze_question(question)
        
        # 提取任务
        tasks = self.extract_tasks(analysis_result)
        
        # 优先级排序
        prioritized_tasks = self.prioritize_tasks(tasks, analysis_result)
        
        # 格式化输出
        return self.format_todo_list(prioritized_tasks, format_type, title)
    

    
    # 以下是内部辅助方法
    
    def _extract_main_theme(self, question: str) -> str:
        """提取问题的主题
        
        使用预编译的正则表达式提高性能，避免重复编译模式。
        
        Args:
            question: 用户问题文本
            
        Returns:
            提取的主题字符串
        """
        # 使用预编译的正则表达式提高性能
        for pattern in self.theme_patterns_regex:
            match = pattern.search(question)
            if match:
                return match.group(1)
        
        return "未明确指定的任务"
        
    def _extract_subtasks(self, question: str) -> List[str]:
        """
        从问题中提取子任务
        
        Args:
            question: 用户问题文本
            
        Returns:
            子任务列表
        """
        # 查找包含特定标记的子任务
        subtask_markers = ['包含', '包括', '具有', '有', '需', '需要']
        subtasks = []
        
        try:
            for marker in subtask_markers:
                if marker in question:
                    # 提取标记后的内容
                    marker_index = question.find(marker)
                    rest = question[marker_index + len(marker):].strip()
                    
                    # 使用预编译的正则表达式分割可能的多个子任务
                    if self.delimiter_pattern.search(rest):
                        split_rest = self.delimiter_pattern.split(rest)
                        subtasks.extend([task.strip() for task in split_rest if task.strip()])
                    elif '和' in rest:
                        split_rest = self.connector_pattern.split(rest)
                        subtasks.extend([task.strip() for task in split_rest if task.strip()])
                    else:
                        # 如果没有明显的分隔符，尝试提取到句子结束
                        end_match = self.end_punctuation_pattern.search(rest)
                        if end_match:
                            subtasks.append(rest[:end_match.start()].strip())
                        else:
                            subtasks.append(rest.strip())
                    break  # 找到一个标记后就退出，避免重复提取
        except Exception as e:
            logger.warning(f"提取子任务时出错: {e}")
            # 返回一个默认任务，确保不会因为异常而返回空列表
            subtasks = ["执行核心任务"]
        
        # 移除空的子任务
        subtasks = [task for task in subtasks if task]
        return subtasks
    
    def _extract_parallel_tasks(self, question: str) -> List[str]:
        """
        从问题中提取并列任务（通过逗号、顿号或'和'连接的任务）
        
        Args:
            question: 用户问题文本
            
        Returns:
            并列任务列表
        """
        # 查找并列结构的模式
        parallel_tasks = []
        
        # 检查是否有"包含"、"包括"等标记后面的并列内容（这是最常见的子任务模式）
        subtask_markers = ['包含', '包括', '具有', '有']
        for marker in subtask_markers:
            if marker in question:
                # 提取标记后面的内容
                marker_pos = question.find(marker)
                content_after_marker = question[marker_pos + len(marker):].strip()
                
                # 处理'和'连接的情况，优先分割
                if '和' in content_after_marker:
                    # 分割成多个部分
                    parts = []
                    for part in re.split(r'和', content_after_marker):
                        part = part.strip()
                        # 再次检查是否有顿号或逗号
                        if '、' in part or ',' in part:
                            subparts = re.split(r'[、,]', part)
                            parts.extend([p.strip() for p in subparts if p.strip()])
                        else:
                            parts.append(part)
                    
                    # 清理并过滤非空项目
                    cleaned_items = [item for item in parts if item]
                    
                    # 如果有多个项目，认为是并列任务
                    if len(cleaned_items) >= 2:
                        parallel_tasks = cleaned_items
                        return parallel_tasks
                
                # 处理顿号和逗号
                if '、' in content_after_marker or ',' in content_after_marker:
                    # 优先使用顿号和逗号分割
                    items = re.split(r'[、,]', content_after_marker)
                    
                    # 清理并过滤非空项目
                    cleaned_items = [item.strip() for item in items if item.strip()]
                    
                    # 进一步处理'和'连接的内容
                    final_items = []
                    for item in cleaned_items:
                        if '和' in item:
                            final_items.extend([i.strip() for i in item.split('和') if i.strip()])
                        else:
                            final_items.append(item)
                    
                    # 如果有多个项目，认为是并列任务
                    if len(final_items) >= 2:
                        parallel_tasks = final_items
                        return parallel_tasks
                break
        
        # 如果没有找到包含标记，检查整个问题中的并列结构
        if not parallel_tasks:
            # 首先处理'和'连接的并列任务
            if '和' in question and len(question) > 5:  # 确保问题长度合理
                # 尝试提取主语部分（假设在第一个'和'之前）
                first_and_pos = question.find('和')
                potential_subject = question[:first_and_pos].strip()
                
                # 如果主语部分包含动作词，可能是并列任务
                for action_type, words in self.task_keywords.items():
                    action_found = False
                    for word in words:
                        if word in potential_subject:
                            action_found = True
                            break
                    if action_found:
                        # 分割并列任务
                        all_parts = re.split(r'和', question)
                        cleaned_parts = [part.strip() for part in all_parts if part.strip()]
                        if len(cleaned_parts) >= 2:
                            parallel_tasks = cleaned_parts
                            return parallel_tasks
                        break
        
        # 最后检查逗号和顿号分割的结构
        if not parallel_tasks and ('，' in question or '、' in question):
            # 分割句子
            parts = re.split(r'[，、]', question)
            # 清理每个部分
            cleaned_parts = [part.strip() for part in parts if part.strip()]
            
            # 检查是否有明确的动作词在各部分
            action_words = set()
            for part in cleaned_parts:
                for action_type, words in self.task_keywords.items():
                    for word in words:
                        if word in part:
                            action_words.add(word)
            
            # 如果多个部分都包含动作词，认为是并列任务
            if len(action_words) >= 1 and len(cleaned_parts) >= 2:
                parallel_tasks = cleaned_parts
        
        return parallel_tasks
    
    def _clean_task_description(self, task_desc: str) -> str:
        """
        清理任务描述，移除多余的标点和连接词
        
        Args:
            task_desc: 原始任务描述
            
        Returns:
            清理后的任务描述
        """
        # 使用预编译的正则表达式移除多余的标点
        task_desc = self.punctuation_pattern.sub('', task_desc).strip()
        
        # 移除常见的连接词
        connectors = ['并且', '而且', '还有', '然后', '另外', '同时']
        for connector in connectors:
            task_desc = task_desc.replace(connector, '').strip()
        
        return task_desc
    
    def _is_duplicate_task(self, task_content: str, existing_tasks: List[Dict[str, str]]) -> bool:
        """
        检查任务是否与已存在的任务重复
        
        Args:
            task_content: 待检查的任务内容
            existing_tasks: 已存在的任务列表
            
        Returns:
            是否重复
        """
        # 简单的重复检测，检查是否完全匹配或包含关系
        for task in existing_tasks:
            existing_content = task['content']
            # 如果内容完全相同，或者一个内容是另一个的子集且长度差异不大，认为是重复
            if task_content == existing_content or \
               (task_content in existing_content and len(task_content) > 0.7 * len(existing_content)) or \
               (existing_content in task_content and len(existing_content) > 0.7 * len(task_content)):
                return True
        return False
        
    def _determine_initial_priority(self, priority_indicators: List[str]) -> str:
        """
        根据优先级指示词确定任务的初始优先级
        
        Args:
            priority_indicators: 优先级指示词列表
            
        Returns:
            优先级字符串
        """
        # 默认优先级
        priority = 'medium'
        
        # 检查是否有高优先级指示词
        for high_keyword in self.priority_keywords['high']:
            if high_keyword in priority_indicators:
                priority = 'high'
                break
        
        # 如果没有高优先级指示词，检查是否有低优先级指示词
        if priority == 'medium':
            for low_keyword in self.priority_keywords['low']:
                if low_keyword in priority_indicators:
                    priority = 'low'
                    break
        
        return priority
    
    def _extract_key_actions(self, question: str) -> List[str]:
        """提取问题中的关键动作词"""
        key_actions = []
        
        for action_type, keywords in self.task_keywords.items():
            for keyword in keywords:
                if keyword in question:
                    key_actions.append(keyword)
        
        return key_actions
    
    def _extract_priority_indicators(self, question: str) -> List[str]:
        """提取问题中的优先级指示词"""
        indicators = []
        
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in question:
                    indicators.append(keyword)
        
        return indicators
    
    def _identify_dependencies(self, question: str) -> List[Dict[str, str]]:
        """识别任务之间的依赖关系"""
        dependencies = []
        
        # 简单的依赖关系识别，可以根据需要扩展
        for dep_type, patterns in self.dependency_patterns.items():
            for pattern in patterns:
                if pattern in question:
                    dependencies.append({
                        'type': dep_type,
                        'pattern': pattern
                    })
        
        return dependencies
    
    def _generate_task_description(self, question: str, keyword: str, action_type: str) -> str:
        """基于关键词和动作类型生成任务描述"""
        # 查找关键词前后的上下文，生成更具体的任务描述
        # 这是一个简单实现，可以根据需要扩展为更复杂的NLP处理
        
        # 尝试提取关键词相关的宾语
        keyword_index = question.find(keyword)
        if keyword_index != -1:
            # 截取关键词后的部分
            remaining_text = question[keyword_index + len(keyword):].strip()
            
            # 查找第一个标点符号或结束
            end_positions = [remaining_text.find(p) for p in ["，", "。", "！", "？", "；", "："] if remaining_text.find(p) != -1]
            if end_positions:
                end_pos = min(end_positions)
                task_detail = remaining_text[:end_pos].strip()
            else:
                task_detail = remaining_text.strip()
            
            # 如果找到了具体内容，构建任务描述
            if task_detail:
                return f"{keyword}{task_detail}"
        
        # 默认任务描述
        return f"{keyword}{action_type}相关内容"
    
    def _generate_default_tasks(self, question: str) -> List[Dict[str, str]]:
        """当无法通过关键词提取任务时，生成默认任务列表"""
        default_tasks = [
            {
                'content': f"分析用户请求：{question}",
                'priority': 'high',
                'status': 'pending',
                'id': '1'
            },
            {
                'content': "制定详细的实施计划",
                'priority': 'high',
                'status': 'pending',
                'id': '2'
            },
            {
                'content': "执行计划中的具体步骤",
                'priority': 'medium',
                'status': 'pending',
                'id': '3'
            },
            {
                'content': "验证结果并进行必要的调整",
                'priority': 'medium',
                'status': 'pending',
                'id': '4'
            }
        ]
        
        return default_tasks
    
    def _sort_by_dependencies(self, tasks: List[Dict[str, str]], dependencies: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """根据依赖关系对任务进行排序"""
        # 简单的排序实现，实际使用中可能需要更复杂的图算法
        # 这里我们基于关键词简单排序：分析/设计 -> 实现 -> 测试 -> 文档
        
        # 定义任务类型的优先级顺序
        action_order = {
            '分析': 0,
            '设计': 1,
            '实现': 2,
            '修复': 2,  # 修复与实现优先级相同
            '测试': 3,
            '优化': 4,
            '文档': 5
        }
        
        # 根据任务描述中的动作类型进行排序
        def get_task_priority(task):
            content = task['content']
            for action, order in action_order.items():
                if action in content:
                    return order
            # 默认优先级
            return len(action_order)
        
        sorted_tasks = sorted(tasks, key=get_task_priority)
        
        # 检查是否有前置依赖关键词，确保这些任务在前面
        for dep in dependencies:
            if dep['type'] == '前置' and dep['pattern'] in tasks[0]['content']:
                # 已经在最前面，不需要调整
                pass
            elif dep['type'] == '前置':
                # 查找包含前置依赖模式的任务并移到前面
                for i, task in enumerate(sorted_tasks):
                    if dep['pattern'] in task['content']:
                        # 将找到的任务移到列表开头
                        priority_task = sorted_tasks.pop(i)
                        sorted_tasks.insert(0, priority_task)
                        break
        
        return sorted_tasks


# 导出的便捷函数
def generate_todo_from_question(question: str, format_type: str = 'json', title: str = None) -> str:
    """
    从用户问题生成任务列表的便捷函数
    
    Args:
        question: 用户输入的问题
        format_type: 输出格式类型，支持 'json', 'text', 'markdown', 'simple', 'html'
        title: 可选的任务列表标题
        
    Returns:
        格式化的任务列表字符串
        
    Raises:
        ValueError: 当输入参数无效时
        Exception: 当生成任务列表失败时
    """
    # 参数验证
    if not question or not isinstance(question, str):
        raise ValueError("问题必须是有效的非空字符串")
    
    supported_formats = ['json', 'text', 'markdown', 'simple', 'html']
    if format_type not in supported_formats:
        raise ValueError(f"不支持的格式类型: {format_type}。支持的格式有: {', '.join(supported_formats)}")
    
    try:
        # 创建生成器实例
        generator = TodoListGenerator()
        # 生成并返回任务列表
        return generator.generate_todo_list(question, format_type, title)
    except Exception as e:
        logger.error(f"生成任务列表失败: {str(e)}")
        # 返回一个简单的错误提示
        if format_type == 'json':
            import json
            return json.dumps({'error': f'生成任务列表失败: {str(e)}'}, ensure_ascii=False, indent=2)
        elif format_type == 'markdown':
            return f"# 错误\n\n生成任务列表失败: {str(e)}"
        else:
            return f"错误: 生成任务列表失败: {str(e)}"


# 测试函数
def test_todo_list_generator():
    """测试任务列表生成器的功能"""
    generator = TodoListGenerator()
    
    # 测试用例
    test_questions = [
        "我需要开发一个能够精准分析用户问题并生成结构化to do list列表的功能模块",
        "请优化系统性能，首先分析当前瓶颈，然后实现优化方案，最后进行测试",
        "紧急：修复登录页面的bug，必须在今天完成"
    ]
    
    # 测试的输出格式
    test_formats = ['json', 'text', 'markdown', 'simple']
    
    print("===== 任务列表生成器测试 =====")
    for i, question in enumerate(test_questions):
        print(f"\n\n=== 测试用例 {i+1}: {question} ===")
        
        # 为每个问题生成带自定义标题的任务列表
        custom_title = f"任务清单 #{i+1}"
        
        # 测试各种格式
        for format_type in test_formats:
            print(f"\n\n--- {format_type.upper()} 格式输出 (带自定义标题): ---")
            result = generator.generate_todo_list(question, format_type=format_type, title=custom_title)
            
            # 对于JSON和简单格式，完整输出
            if format_type in ['json', 'simple']:
                print(result)
            else:
                # 对于其他格式，只显示前300个字符以避免输出过长
                preview = result[:300] + ('...' if len(result) > 300 else '')
                print(preview)
        
        print("\n" + "=" * 60)
    
    # 单独测试HTML格式，但不输出完整内容
    print("\n\n=== 额外测试: HTML格式 ===")
    html_result = generator.generate_todo_list(test_questions[0], format_type='html', title="HTML格式测试")
    print(f"HTML生成成功，内容长度: {len(html_result)} 字符")
    print("HTML前100个字符预览:")
    print(html_result[:100] + "...")


if __name__ == "__main__":
    # 直接运行时显示使用说明
    import sys
    
    if len(sys.argv) > 1:
        # 如果有命令行参数，将第一个参数作为问题
        question = ' '.join(sys.argv[1:])
        format_type = 'markdown'  # 默认使用markdown格式
        
        print(f"\n基于问题生成任务列表:\n{question}\n")
        print("=" * 80)
        result = generate_todo_from_question(question, format_type=format_type)
        print(result)
    else:
        # 否则运行测试
        print("\n=== 电脑操作专家AI助手 - 任务列表生成器 ===\n")
        print("使用方法:")
        print("  1. 作为模块导入: from todo_list_generator import generate_todo_from_question")
        print("  2. 命令行使用: python todo_list_generator.py '您的问题描述'")
        print("  3. 直接运行查看测试结果\n")
        print("运行测试用例...\n")
        test_todo_list_generator()
