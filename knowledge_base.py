import json
import os
from datetime import datetime
import hashlib
from typing import List, Dict, Optional, Any

class KnowledgeBase:
    def __init__(self):
        self.knowledge_base_file = "knowledge_base.json"
        self.versions_dir = "knowledge_base_versions"
        self.attachments_dir = "knowledge_base_attachments"
        self.data = {
            "metadata": {
                "name": "AI助手知识库",
                "description": "结构化知识库，包含领域专业知识、任务执行流程、常见问题解决方案和最佳实践案例",
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat()
            },
            "categories": [
                {"id": "1", "name": "领域专业知识", "description": "电脑操作相关的专业知识"},
                {"id": "2", "name": "任务执行流程", "description": "各种任务的标准执行流程"},
                {"id": "3", "name": "常见问题解决方案", "description": "常见问题的解决方法"},
                {"id": "4", "name": "最佳实践案例", "description": "最佳实践和成功案例"}
            ],
            "tags": [
                {"id": "1", "name": "Windows", "description": "Windows系统相关"},
                {"id": "2", "name": "文件操作", "description": "文件和文件夹操作"},
                {"id": "3", "name": "系统设置", "description": "系统设置和配置"},
                {"id": "4", "name": "故障排除", "description": "故障诊断和修复"},
                {"id": "5", "name": "工具使用", "description": "工具和软件使用"}
            ],
            "knowledge_items": [],
            "relations": []
        }
        
        # 初始化目录结构
        self._init_directories()
        # 加载知识库数据
        self._load_data()
    
    def _init_directories(self):
        """初始化目录结构"""
        for dir_path in [self.versions_dir, self.attachments_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
    
    def _load_data(self):
        """加载知识库数据"""
        if os.path.exists(self.knowledge_base_file):
            try:
                with open(self.knowledge_base_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"加载知识库失败: {e}")
    
    def _save_data(self):
        """保存知识库数据"""
        try:
            # 更新最后修改时间
            self.data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # 保存到主文件
            with open(self.knowledge_base_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            
            # 创建版本备份
            self._create_version_backup()
        except Exception as e:
            print(f"保存知识库失败: {e}")
    
    def _create_version_backup(self):
        """创建版本备份"""
        version_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_file = os.path.join(self.versions_dir, f"kb_{version_timestamp}.json")
        
        with open(version_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        # 只保留最近10个版本
        self._cleanup_old_versions()
    
    def _cleanup_old_versions(self):
        """清理旧版本，只保留最近10个"""
        version_files = sorted(
            [f for f in os.listdir(self.versions_dir) if f.startswith("kb_")],
            reverse=True
        )
        
        for old_file in version_files[10:]:
            os.remove(os.path.join(self.versions_dir, old_file))
    
    def _generate_id(self, text: str) -> str:
        """生成唯一ID"""
        return hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
    
    # 知识条目管理
    def add_knowledge_item(self, item_data: Dict[str, Any]) -> str:
        """添加知识条目"""
        # 生成唯一ID
        item_id = self._generate_id(item_data.get("title", ""))
        
        # 创建知识条目
        knowledge_item = {
            "id": item_id,
            "title": item_data.get("title", ""),
            "content": item_data.get("content", ""),
            "category_id": item_data.get("category_id", "1"),
            "tags": item_data.get("tags", []),
            "type": item_data.get("type", "text"),  # text, image, code, multimodal
            "attachments": item_data.get("attachments", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "views": 0,
            "rating": 0,
            "author": item_data.get("author", "system")
        }
        
        self.data["knowledge_items"].append(knowledge_item)
        self._save_data()
        return item_id
    
    def update_knowledge_item(self, item_id: str, update_data: Dict[str, Any]) -> bool:
        """更新知识条目"""
        for item in self.data["knowledge_items"]:
            if item["id"] == item_id:
                # 更新字段
                for key, value in update_data.items():
                    if key in item:
                        item[key] = value
                
                # 更新修改时间
                item["updated_at"] = datetime.now().isoformat()
                self._save_data()
                return True
        return False
    
    def delete_knowledge_item(self, item_id: str) -> bool:
        """删除知识条目"""
        initial_length = len(self.data["knowledge_items"])
        self.data["knowledge_items"] = [
            item for item in self.data["knowledge_items"] if item["id"] != item_id
        ]
        
        if len(self.data["knowledge_items"]) < initial_length:
            self._save_data()
            return True
        return False
    
    def get_knowledge_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """获取单个知识条目"""
        for item in self.data["knowledge_items"]:
            if item["id"] == item_id:
                # 增加浏览次数
                item["views"] += 1
                self._save_data()
                return item
        return None
    
    def search_knowledge_items(self, query: str, category_id: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """搜索知识条目"""
        results = []
        query_lower = query.lower()
        
        for item in self.data["knowledge_items"]:
            # 检查分类
            if category_id and item["category_id"] != category_id:
                continue
            
            # 检查标签
            if tags:
                if not any(tag in item["tags"] for tag in tags):
                    continue
            
            # 检查标题和内容
            if query_lower in item["title"].lower() or query_lower in item["content"].lower():
                results.append(item)
        
        # 按浏览次数和更新时间排序
        results.sort(key=lambda x: (x["views"], x["updated_at"]), reverse=True)
        return results
    
    # 分类管理
    def add_category(self, name: str, description: str) -> str:
        """添加分类"""
        category_id = self._generate_id(name)
        category = {
            "id": category_id,
            "name": name,
            "description": description
        }
        self.data["categories"].append(category)
        self._save_data()
        return category_id
    
    def update_category(self, category_id: str, name: str, description: str) -> bool:
        """更新分类"""
        for category in self.data["categories"]:
            if category["id"] == category_id:
                category["name"] = name
                category["description"] = description
                self._save_data()
                return True
        return False
    
    def delete_category(self, category_id: str) -> bool:
        """删除分类"""
        # 检查是否有知识条目使用该分类
        for item in self.data["knowledge_items"]:
            if item["category_id"] == category_id:
                return False
        
        initial_length = len(self.data["categories"])
        self.data["categories"] = [
            category for category in self.data["categories"] if category["id"] != category_id
        ]
        
        if len(self.data["categories"]) < initial_length:
            self._save_data()
            return True
        return False
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """获取所有分类"""
        return self.data["categories"]
    
    # 标签管理
    def add_tag(self, name: str, description: str) -> str:
        """添加标签"""
        tag_id = self._generate_id(name)
        tag = {
            "id": tag_id,
            "name": name,
            "description": description
        }
        self.data["tags"].append(tag)
        self._save_data()
        return tag_id
    
    def update_tag(self, tag_id: str, name: str, description: str) -> bool:
        """更新标签"""
        for tag in self.data["tags"]:
            if tag["id"] == tag_id:
                tag["name"] = name
                tag["description"] = description
                self._save_data()
                return True
        return False
    
    def delete_tag(self, tag_id: str) -> bool:
        """删除标签"""
        initial_length = len(self.data["tags"])
        self.data["tags"] = [
            tag for tag in self.data["tags"] if tag["id"] != tag_id
        ]
        
        if len(self.data["tags"]) < initial_length:
            self._save_data()
            return True
        return False
    
    def get_tags(self) -> List[Dict[str, Any]]:
        """获取所有标签"""
        return self.data["tags"]
    
    # 知识关联管理
    def add_relation(self, source_id: str, target_id: str, relation_type: str) -> str:
        """添加知识关联"""
        relation_id = self._generate_id(f"{source_id}_{target_id}_{relation_type}")
        relation = {
            "id": relation_id,
            "source_id": source_id,
            "target_id": target_id,
            "type": relation_type,  # related_to, part_of, prerequisite, solution_to
            "created_at": datetime.now().isoformat()
        }
        self.data["relations"].append(relation)
        self._save_data()
        return relation_id
    
    def get_related_items(self, item_id: str, relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取相关知识条目"""
        related_ids = set()
        
        for relation in self.data["relations"]:
            if relation["source_id"] == item_id:
                if not relation_type or relation["type"] == relation_type:
                    related_ids.add(relation["target_id"])
            elif relation["target_id"] == item_id:
                if not relation_type or relation["type"] == relation_type:
                    related_ids.add(relation["source_id"])
        
        return [item for item in self.data["knowledge_items"] if item["id"] in related_ids]
    
    # 高级检索
    def advanced_search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """高级搜索"""
        if filters is None:
            filters = {}
        
        results = self.search_knowledge_items(
            query,
            category_id=filters.get("category_id"),
            tags=filters.get("tags")
        )
        
        # 按类型过滤
        if "type" in filters:
            results = [item for item in results if item["type"] == filters["type"]]
        
        # 按时间范围过滤
        if "start_date" in filters:
            results = [item for item in results if item["created_at"] >= filters["start_date"]]
        
        if "end_date" in filters:
            results = [item for item in results if item["created_at"] <= filters["end_date"]]
        
        return results
    
    # 统计信息
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return {
            "total_items": len(self.data["knowledge_items"]),
            "total_categories": len(self.data["categories"]),
            "total_tags": len(self.data["tags"]),
            "total_relations": len(self.data["relations"]),
            "last_updated": self.data["metadata"]["last_updated"],
            "categories_count": {
                category["id"]: len([item for item in self.data["knowledge_items"] if item["category_id"] == category["id"]])
                for category in self.data["categories"]
            },
            "most_viewed": sorted(self.data["knowledge_items"], key=lambda x: x["views"], reverse=True)[:5],
            "recent_items": sorted(self.data["knowledge_items"], key=lambda x: x["created_at"], reverse=True)[:5]
        }
    
    # 导出/导入功能
    def export_knowledge_base(self, export_path: str) -> bool:
        """导出知识库"""
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出知识库失败: {e}")
            return False
    
    def import_knowledge_base(self, import_path: str) -> bool:
        """导入知识库"""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                imported_data = json.load(f)
            
            # 合并导入的数据
            if "knowledge_items" in imported_data:
                self.data["knowledge_items"].extend(imported_data["knowledge_items"])
            
            if "categories" in imported_data:
                self.data["categories"].extend(imported_data["categories"])
            
            if "tags" in imported_data:
                self.data["tags"].extend(imported_data["tags"])
            
            if "relations" in imported_data:
                self.data["relations"].extend(imported_data["relations"])
            
            self._save_data()
            return True
        except Exception as e:
            print(f"导入知识库失败: {e}")
            return False

# 全局知识库实例
knowledge_base = KnowledgeBase()
