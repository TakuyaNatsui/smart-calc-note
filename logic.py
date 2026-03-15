import re
import math

class CalculatorLogic:
    def __init__(self):
        # 演算子の優先順位と結合性 (True: 右結合, False: 左結合)
        self.operators = {
            '+': (1, False),
            '-': (1, False),
            '*': (2, False),
            '/': (2, False),
            '^': (3, True)
        }
        self.functions = {'sin', 'cos', 'tan', 'log', 'ln', 'sqrt'}
        # 組み込み定数
        self.constants = {'π': math.pi, 'e': math.e}
        # ユーザー定義変数を保持する辞書
        self.variables = {}

    def tokenize(self, expression):
        """数式をトークンに分割する。指数表記、変数名、関数名に対応。"""
        # 正規表現パターン: 
        # 1. 数値 (指数表記含む): \d+\.?\d*(?:[eE][+-]?\d+)?
        # 2. 関数名または変数名: [a-zA-Z_]\w*
        # 3. 演算子・括弧・特殊定数: [+\-*/\^()]|π
        pattern = r'(\d+\.?\d*(?:[eE][+-]?\d+)?|[a-zA-Z_]\w*|π|[+\-*/\^()])'
        raw_tokens = re.findall(pattern, expression.replace(' ', ''))
        
        processed_expr = []
        last_token = '('
        
        for token in raw_tokens:
            # 単項マイナスの処理: 式の先頭、または演算子・左括弧の直後の '-' を '_' に変換
            if token == '-' and last_token in ('(', '+', '-', '*', '/', '^'):
                processed_expr.append('_')
            else:
                processed_expr.append(token)
            last_token = token
        
        return processed_expr

    def shunting_yard(self, tokens):
        """操車場アルゴリズム: 中置記法を逆ポーランド記法 (RPN) に変換する"""
        output_queue = []
        operator_stack = []
        
        # 単項マイナス用の優先順位
        ops = self.operators.copy()
        ops['_'] = (4, True)

        for token in tokens:
            if self._is_numeric_val(token):
                # 数値、定数、または定義済み変数の場合
                val = self._resolve_value(token)
                output_queue.append(val)
            elif token in self.functions:
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output_queue.append(operator_stack.pop())
                if not operator_stack:
                    raise ValueError("括弧が一致しません")
                operator_stack.pop() # '(' を取り除く
                if operator_stack and operator_stack[-1] in self.functions:
                    output_queue.append(operator_stack.pop())
            elif token in ops:
                p1, a1 = ops[token]
                while operator_stack and operator_stack[-1] in ops:
                    op2 = operator_stack[-1]
                    p2, a2 = ops[op2]
                    # 優先順位と結合性の判定
                    if (not a1 and p1 <= p2) or (a1 and p1 < p2):
                        output_queue.append(operator_stack.pop())
                    else:
                        break
                operator_stack.append(token)
            else:
                # 定義されていない変数名などの場合
                raise ValueError(f"未知のシンボルです: {token}")
        
        while operator_stack:
            if operator_stack[-1] == '(':
                raise ValueError("括弧が不一致です")
            output_queue.append(operator_stack.pop())
        
        return output_queue

    def evaluate_rpn(self, rpn_tokens):
        """RPN形式のトークンリストを評価し、数値を算出する"""
        stack = []
        ops_keys = set(self.operators.keys()) | {'_'}

        for token in rpn_tokens:
            if isinstance(token, (int, float)):
                stack.append(float(token))
            elif token == '_': # 単項マイナス
                if not stack: raise ValueError("単項マイナスの対象がありません")
                stack.append(-stack.pop())
            elif token in ops_keys:
                if len(stack) < 2:
                    raise ValueError(f"演算子 '{token}' の引数が不足しています")
                b, a = stack.pop(), stack.pop()
                if token == '+': stack.append(a + b)
                elif token == '-': stack.append(a - b)
                elif token == '*': stack.append(a * b)
                elif token == '/':
                    if b == 0: raise ZeroDivisionError("0で割ることはできません")
                    stack.append(a / b)
                elif token == '^': stack.append(math.pow(a, b))
            elif token in self.functions:
                if len(stack) < 1:
                    raise ValueError(f"関数 '{token}' の引数が不足しています")
                a = stack.pop()
                if token == 'sin': stack.append(math.sin(a))
                elif token == 'cos': stack.append(math.cos(a))
                elif token == 'tan': stack.append(math.tan(a))
                elif token == 'log':
                    if a <= 0: raise ValueError("対数エラー: 値は正である必要があります")
                    stack.append(math.log10(a))
                elif token == 'ln':
                    if a <= 0: raise ValueError("対数エラー: 値は正である必要があります")
                    stack.append(math.log(a))
                elif token == 'sqrt':
                    if a < 0: raise ValueError("平方根エラー: 値は非負である必要があります")
                    stack.append(math.sqrt(a))

        if len(stack) != 1:
            raise ValueError(f"式の評価に失敗しました (スタック残数: {len(stack)})")
        return stack[0]

    def calculate(self, text):
        """複数行のテキスト（代入文および数式）を解析・計算する"""
        lines = text.strip().split('\n')
        last_result = 0
        
        # 組み込み定数で変数を初期化
        current_vars = self.constants.copy()
        # ユーザーがこれまでに定義した変数も反映
        current_vars.update(self.variables)
        
        try:
            for line in lines:
                line = line.split('#')[0].strip() # コメント除去
                if not line: continue
                
                if '=' in line:
                    # 代入文: name = expression
                    parts = line.split('=', 1)
                    var_name = parts[0].strip()
                    expr_str = parts[1].strip()
                    
                    if not re.match(r'^[a-zA-Z_]\w*$', var_name):
                        raise ValueError(f"不正な変数名です: {var_name}")
                    
                    # 式を評価（現在の変数セットを使用）
                    val = self._eval_expr_internal(expr_str, current_vars)
                    current_vars[var_name] = val
                    self.variables[var_name] = val # 永続化
                    last_result = val
                else:
                    # 通常の計算式
                    last_result = self._eval_expr_internal(line, current_vars)
            
            # 結果の整形
            if isinstance(last_result, float) and last_result.is_integer():
                return int(last_result)
            return round(last_result, 10)
        
        except Exception as e:
            return f"エラー: {str(e)}"

    def _eval_expr_internal(self, expression, vars_context):
        """特定の変数コンテキスト下で単一の式を評価する"""
        self._temp_vars = vars_context # 解析中に参照する変数
        tokens = self.tokenize(expression)
        rpn = self.shunting_yard(tokens)
        return self.evaluate_rpn(rpn)

    def _is_numeric_val(self, token):
        """トークンが数値、定数、または変数として評価可能か判定"""
        if token in self._temp_vars: return True
        try:
            float(token)
            return True
        except ValueError:
            return False

    def _resolve_value(self, token):
        """トークンを数値に変換（変数の置換を含む）"""
        if token in self._temp_vars:
            return self._temp_vars[token]
        return float(token)
