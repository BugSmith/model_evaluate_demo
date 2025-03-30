"""
GSM8K数据集实现
"""
import os
import json
import requests
from model_evaluate_demo.utils.registry import DATASETS
from model_evaluate_demo.datasets.base import BaseDataset


@DATASETS.register('gsm8k')
class GSM8KDataset(BaseDataset):
    """
    GSM8K数据集
    
    GSM8K是一个由8.5K个高质量Grade School数学问题组成的数据集，这些问题需要2到8个步骤来解决。
    """
    def __init__(self, **kwargs):
        super().__init__('gsm8k', **kwargs)
        self.subset = kwargs.get('subset', 'main')
        self.max_samples = kwargs.get('max_samples', None)
        
        # 定义默认提示模板
        self.default_template = kwargs.get('template', 
            "问题: {question}\n\n请一步步思考，最后给出答案。"
        )
        
        # 定义URLs
        self.urls = {
            'train': 'https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/train.jsonl',
            'test': 'https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl'
        }
        
    def load(self):
        """加载GSM8K数据集"""
        cache_key = f"gsm8k_{self.subset}_{self.split}"
        
        # 尝试从缓存加载
        cached_data = self.load_from_cache(cache_key)
        if cached_data is not None:
            self.data = cached_data
            return self
        
        # 如果指定了本地数据路径
        if self.data_path and os.path.exists(self.data_path):
            return self._load_from_local()
        
        # 否则从URL下载
        return self._load_from_url()
    
    def _load_from_local(self):
        """从本地加载数据"""
        try:
            file_path = os.path.join(self.data_path, f"{self.split}.jsonl")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"找不到文件: {file_path}")
                
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    item = json.loads(line.strip())
                    processed_item = self._process_item(item)
                    data.append(processed_item)
                    
            if self.max_samples and len(data) > self.max_samples:
                data = data[:self.max_samples]
                
            self.data = data
            
            # 保存到缓存
            cache_key = f"gsm8k_{self.subset}_{self.split}"
            self.save_to_cache(cache_key, data)
            
            print(f"从本地加载了 {len(data)} 个GSM8K样本")
            return self
            
        except Exception as e:
            print(f"从本地加载GSM8K数据集失败: {str(e)}")
            raise
    
    def _load_from_url(self):
        """从URL下载数据"""
        try:
            if self.split not in self.urls:
                raise ValueError(f"分割'{self.split}'不可用。可用的分割: {list(self.urls.keys())}")
                
            url = self.urls[self.split]
            print(f"从URL下载GSM8K数据: {url}")
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = []
            for line in response.text.splitlines():
                if line.strip():
                    item = json.loads(line.strip())
                    processed_item = self._process_item(item)
                    data.append(processed_item)
            
            if self.max_samples and len(data) > self.max_samples:
                data = data[:self.max_samples]
                
            self.data = data
            
            # 保存到缓存
            cache_key = f"gsm8k_{self.subset}_{self.split}"
            self.save_to_cache(cache_key, data)
            
            print(f"从URL加载了 {len(data)} 个GSM8K样本")
            return self
            
        except Exception as e:
            print(f"从URL加载GSM8K数据集失败: {str(e)}")
            raise
    
    def _process_item(self, item):
        """处理原始数据项"""
        # 提取问题和答案
        question = item.get('question', '')
        answer = item.get('answer', '')
        
        # 提取最终的数值答案
        final_answer = self._extract_final_answer(answer)
        
        return {
            'question': question,
            'full_answer': answer,
            'answer': final_answer
        }
    
    def _extract_final_answer(self, answer_text):
        """从答案文本中提取最终的数值答案"""
        try:
            # GSM8K通常在答案的最后一行包含"The answer is X"
            lines = answer_text.strip().split('\n')
            last_line = lines[-1].strip()
            
            # 尝试提取"The answer is X"模式
            if "answer is" in last_line.lower():
                parts = last_line.lower().split("answer is")
                if len(parts) > 1:
                    # 提取数字部分
                    number_part = parts[1].strip()
                    # 移除美元符号等
                    for char in ['$', ',', '\\$']:
                        number_part = number_part.replace(char, '')
                    # 移除后面的句号或其他非数字字符
                    import re
                    matches = re.findall(r'-?\d+\.?\d*', number_part)
                    if matches:
                        return matches[0]
            
            # 如果上面的方法不成功，尝试查找最后出现的数字
            import re
            all_numbers = re.findall(r'-?\d+\.?\d*', answer_text)
            if all_numbers:
                return all_numbers[-1]
                
            return answer_text  # 如果无法提取，返回原始答案
            
        except Exception:
            return answer_text 