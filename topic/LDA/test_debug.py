#coding='utf-8'
import os
import time
import datetime

# 测试调试输出功能
def test_debug_output():
    print("=" * 60)
    print("[INFO] 调试输出测试程序启动")
    print(f"[INFO] 开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 测试文件读取
    print("\n[阶段1] 测试文件读取")
    print("[DEBUG] 开始读取文件: ./qx_分词结果.txt")
    start_time = time.time()
    
    # 只读取前几行进行测试
    try:
        with open('./qx_分词结果.txt', 'r', encoding='utf8') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= 10:  # 只读取前10行
                    break
                lines.append(line.strip())
        
        end_time = time.time()
        print(f"[DEBUG] 文件读取完成，共读取 {len(lines)} 行")
        print(f"[DEBUG] 读取耗时: {end_time - start_time:.2f} 秒")
        
        # 显示前几行内容
        print("[DEBUG] 前3行内容预览:")
        for i, line in enumerate(lines[:3]):
            print(f"  行{i+1}: {line[:50]}...")
            
    except Exception as e:
        print(f"[ERROR] 文件读取失败: {e}")
        return
    
    # 测试数据处理
    print("\n[阶段2] 测试数据处理")
    print("[DEBUG] 模拟数据处理过程...")
    
    # 模拟一些数据处理
    train = []
    for line in lines:
        if line:
            words = line.split(' ')
            train.append([w for w in words if w])
    
    print(f"[DEBUG] 处理完成，训练数据样本数: {len(train)}")
    
    # 测试统计信息
    print("\n[阶段3] 测试统计信息")
    if train:
        doc_lengths = [len(doc) for doc in train]
        print(f"[DEBUG] 平均文档长度: {sum(doc_lengths) / len(doc_lengths):.2f} 词")
        print(f"[DEBUG] 最短文档: {min(doc_lengths)} 词")
        print(f"[DEBUG] 最长文档: {max(doc_lengths)} 词")
    
    print("\n" + "=" * 60)
    print("[INFO] 调试输出测试完成")
    print(f"[INFO] 完成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == '__main__':
    test_debug_output()