"""
准确率评估指标实现
"""
import re
from model_evaluate_demo.utils.registry import METRICS
from model_evaluate_demo.metrics.base import BaseMetric


@METRICS.register('accuracy')
class AccuracyMetric(BaseMetric):
    """
    准确率评估指标
    
    从生成文本中提取数值答案，并与参考答案比较。
    """
    def __init__(self):
        super().__init__('accuracy')
        
    def compute(self, predictions, references, **kwargs):
        """
        计算准确率
        
        Args:
            predictions: 模型生成的文本列表
            references: 参考答案列表
            **kwargs: 
                - answer_pattern: 从生成文本中提取答案的正则表达式模式
                - normalize: 是否对答案进行归一化处理
                - debug: 是否输出调试信息
                
        Returns:
            dict: 包含准确率和详细信息的字典
        """
        if len(predictions) != len(references):
            raise ValueError(f"预测数量 ({len(predictions)}) 与参考答案数量 ({len(references)}) 不匹配")
        
        answer_pattern = kwargs.get('answer_pattern', None)
        normalize = kwargs.get('normalize', True)
        debug = kwargs.get('debug', False)
        
        if debug:
            print("开始准确率计算...")
        
        # 提取预测答案
        extracted_predictions = []
        for i, pred in enumerate(predictions):
            extracted = self._extract_answer(pred, answer_pattern)
            if normalize:
                extracted = self._normalize_answer(extracted)
                
            if debug:
                print(f"样本 {i}:")
                print(f"  原始生成: {pred[:200]}..." if len(pred) > 200 else f"  原始生成: {pred}")
                print(f"  提取答案: '{extracted}'")
                
            extracted_predictions.append(extracted)
        
        # 归一化参考答案
        normalized_references = []
        for i, ref in enumerate(references):
            norm_ref = ref
            if normalize:
                norm_ref = self._normalize_answer(ref)
                
            if debug:
                print(f"样本 {i} 参考答案: '{ref}' -> 归一化: '{norm_ref}'")
                
            normalized_references.append(norm_ref)
        
        # 计算准确率
        correct = 0
        details = []
        
        for i, (pred, ref) in enumerate(zip(extracted_predictions, normalized_references)):
            # 通过数值比较或字符串包含关系判断正确性
            is_correct = False
            
            # 先尝试精确匹配
            if pred == ref:
                is_correct = True
            else:
                # 检查数值是否相等
                try:
                    pred_num = float(pred.replace('π', 'pi').replace('pi', '3.14159'))
                    ref_num = float(ref.replace('π', 'pi').replace('pi', '3.14159'))
                    is_correct = abs(pred_num - ref_num) < 1e-5
                except (ValueError, TypeError):
                    # 不是数值，尝试字符串包含关系
                    is_correct = pred in ref or ref in pred
            
            if is_correct:
                correct += 1
                
            details.append({
                'index': i,
                'prediction': predictions[i],
                'extracted': extracted_predictions[i],
                'reference': references[i],
                'normalized_reference': normalized_references[i],
                'correct': is_correct
            })
            
            if debug:
                print(f"样本 {i} 判断: {'✓ 正确' if is_correct else '✗ 错误'}")
        
        accuracy = correct / len(predictions) if predictions else 0
        
        if debug:
            print(f"准确率计算完成: {correct}/{len(predictions)} = {accuracy}")
        
        return {
            'score': accuracy,
            'correct': correct,
            'total': len(predictions),
            'details': details
        }
    
    def _extract_answer(self, text, pattern=None):
        """
        从文本中提取答案
        """
        if not text:
            return ""
            
        # 如果提供了模式，使用该模式
        if pattern:
            matches = re.search(pattern, text)
            if matches and matches.groups():
                return matches.group(1).strip()
        
        # 尝试查找boxed答案 (常见于LaTeX格式)
        boxed_pattern = r'\\boxed\{(.*?)\}'
        boxed_matches = re.search(boxed_pattern, text)
        if boxed_matches:
            return boxed_matches.group(1).strip()
        
        # 默认模式：尝试提取"答案是"、"答案："或"答案为"后面的内容
        patterns = [
            r'答案是[:：]?\s*(.+?)(?:\.|。|$)',
            r'答案[:：]\s*(.+?)(?:\.|。|$)',
            r'答案为[:：]?\s*(.+?)(?:\.|。|$)',
            r'the answer is:?\s*(.+?)(?:\.|$)',
            r'answer:?\s*(.+?)(?:\.|$)',
            r'因此答案为:?\s*(.+?)(?:\.|。|$)',
            r'所以答案是:?\s*(.+?)(?:\.|。|$)',
            r'因此答案是:?\s*(.+?)(?:\.|。|$)',
            r'所以答案为:?\s*(.+?)(?:\.|。|$)',
            r'最终答案:?\s*(.+?)(?:\.|。|$)',
            r'最终答案为:?\s*(.+?)(?:\.|。|$)',
            r'最终答案是:?\s*(.+?)(?:\.|。|$)'
        ]
        
        for p in patterns:
            matches = re.search(p, text, re.IGNORECASE)
            if matches:
                return matches.group(1).strip()
                
        # 检查Python代码输出
        code_output_pattern = r'```output\s*\n([\d\.\+\-]+)'
        code_output_matches = re.search(code_output_pattern, text)
        if code_output_matches:
            return code_output_matches.group(1).strip()
            
        # 查找最后一个等式的结果
        equals_pattern = r'=\s*([\d\.\+\-πpi\/\*]+)(?:\s|$|\.|。|,|，)'
        equals_matches = re.findall(equals_pattern, text)
        if equals_matches:
            return equals_matches[-1].strip()
        
        # 如果找不到明确的答案标记，则提取最后一个数字或表达式
        number_matches = re.findall(r'[-+]?[\d\.]+(?:π|pi)?', text)
        if number_matches:
            return number_matches[-1]
            
        # 从最后一行尝试提取答案
        lines = text.strip().split('\n')
        last_line = lines[-1].strip()
        
        # 如果最后一行有数字，提取它
        last_line_numbers = re.findall(r'[-+]?[\d\.]+(?:π|pi)?', last_line)
        if last_line_numbers:
            return last_line_numbers[-1]
            
        # 最后手段：返回文本的最后一行
        return last_line
    
    def _normalize_answer(self, answer):
        """
        归一化答案
        """
        if not answer:
            return ""
            
        # 移除引号、括号和其他干扰字符
        answer = re.sub(r'[「」『』\(\)\[\]\{\}"\'""'']', '', answer)
        
        # 转换为小写
        answer = answer.lower()
        
        # 替换多个空格为单个空格
        answer = re.sub(r'\s+', ' ', answer).strip()
        
        # 处理特殊数学表示
        # 替换特殊数学符号
        answer = (answer.replace('×', '*')
                       .replace('÷', '/')
                       .replace('（', '(')
                       .replace('）', ')')
                       .replace('，', ',')
                       .replace('。', '.'))
        
        # 如果完全是数值形式，尝试统一格式
        if re.match(r'^[-+]?[\d\.]+$', answer):
            try:
                # 尝试转为浮点数再转回字符串，统一格式
                num = float(answer)
                if num.is_integer():
                    # 如果是整数，移除小数点和零
                    answer = str(int(num))
                else:
                    # 浮点数，保留5位小数
                    answer = str(round(num, 5)).rstrip('0').rstrip('.')
            except:
                pass
        
        return answer 