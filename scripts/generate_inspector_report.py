#!/usr/bin/env python3
"""
MCP Inspectorテスト結果のHTMLレポートを生成するスクリプト
"""

import argparse
import json
import os
import glob
import datetime
import sys
from pathlib import Path


def parse_arguments():
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(description='MCP Inspectorテスト結果のHTMLレポートを生成する')
    parser.add_argument('--report-dir', type=str, default='test-reports/mcp-inspector',
                        help='テスト結果が保存されているディレクトリ')
    parser.add_argument('--output', type=str, default='test-reports/mcp-inspector/report.html',
                        help='出力するHTMLファイルのパス')
    parser.add_argument('--title', type=str, default='MCP Inspector テスト結果',
                        help='レポートのタイトル')
    return parser.parse_args()


def find_summary_file(report_dir):
    """最新のサマリーファイルを検索する"""
    summary_files = glob.glob(os.path.join(report_dir, 'suite_summary_*.json'))
    if not summary_files:
        return None
    
    # 最新のファイルを取得
    latest_file = max(summary_files, key=os.path.getmtime)
    return latest_file


def find_report_files(report_dir):
    """レポートファイルを検索する"""
    return glob.glob(os.path.join(report_dir, 'report_*.json'))


def load_json_file(file_path):
    """JSONファイルを読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"エラー: {file_path} の読み込みに失敗しました: {e}", file=sys.stderr)
        return {}


def generate_html_report(summary_file, report_files, output_file, title):
    """HTMLレポートを生成する"""
    # サマリー情報の読み込み
    summary_data = {}
    if summary_file:
        summary_data = load_json_file(summary_file)
    
    # レポートファイルの読み込み
    report_data = []
    for file_path in report_files:
        data = load_json_file(file_path)
        if data:
            # ファイル名からテスト名を抽出
            file_name = os.path.basename(file_path)
            test_name = file_name.replace('report_', '').split('_')[0]
            test_name = test_name.replace('_', ' ')
            
            # テスト結果を追加
            report_data.append({
                'name': test_name,
                'file': file_path,
                'data': data
            })
    
    # 現在の日時
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # HTMLの生成
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .summary {{
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .summary-stats {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin: 20px 0;
        }}
        .stat-box {{
            text-align: center;
            padding: 10px;
            border-radius: 5px;
            min-width: 120px;
            margin: 5px;
        }}
        .total {{
            background-color: #e9ecef;
        }}
        .passed {{
            background-color: #d4edda;
            color: #155724;
        }}
        .failed {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .skipped {{
            background-color: #fff3cd;
            color: #856404;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .success {{
            color: #28a745;
        }}
        .failure {{
            color: #dc3545;
        }}
        .details-btn {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
        }}
        .details-btn:hover {{
            background-color: #0069d9;
        }}
        .test-details {{
            display: none;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            white-space: pre-wrap;
            font-family: monospace;
        }}
        .timestamp {{
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="timestamp">レポート生成日時: {now}</p>
    
    <div class="summary">
        <h2>テスト概要</h2>
"""
    
    # サマリー情報の表示
    if summary_data:
        total = summary_data.get('total', 0)
        passed = summary_data.get('passed', 0)
        failed = summary_data.get('failed', 0)
        skipped = summary_data.get('skipped', 0)
        
        html += f"""
        <div class="summary-stats">
            <div class="stat-box total">
                <h3>合計</h3>
                <p>{total}</p>
            </div>
            <div class="stat-box passed">
                <h3>成功</h3>
                <p>{passed}</p>
            </div>
            <div class="stat-box failed">
                <h3>失敗</h3>
                <p>{failed}</p>
            </div>
            <div class="stat-box skipped">
                <h3>スキップ</h3>
                <p>{skipped}</p>
            </div>
        </div>
"""
    else:
        # サマリーファイルがない場合は、レポートファイルから集計
        total = len(report_data)
        passed = sum(1 for r in report_data if r['data'].get('success', 0) > 0 and r['data'].get('failure', 0) == 0)
        failed = total - passed
        
        html += f"""
        <div class="summary-stats">
            <div class="stat-box total">
                <h3>合計</h3>
                <p>{total}</p>
            </div>
            <div class="stat-box passed">
                <h3>成功</h3>
                <p>{passed}</p>
            </div>
            <div class="stat-box failed">
                <h3>失敗</h3>
                <p>{failed}</p>
            </div>
        </div>
"""
    
    html += """
    </div>
    
    <h2>テスト結果詳細</h2>
    <table>
        <thead>
            <tr>
                <th>テスト名</th>
                <th>結果</th>
                <th>詳細</th>
            </tr>
        </thead>
        <tbody>
"""
    
    # テスト結果の表示
    for i, report in enumerate(report_data):
        name = report.get('name', f'テスト {i+1}')
        data = report.get('data', {})
        success = data.get('success', 0)
        failure = data.get('failure', 0)
        
        if success > 0 and failure == 0:
            result = f'<span class="success">成功 ✅</span>'
        else:
            result = f'<span class="failure">失敗 ❌</span>'
        
        html += f"""
        <tr>
            <td>{name}</td>
            <td>{result}</td>
            <td><button class="details-btn" onclick="toggleDetails('details-{i}')">詳細を表示</button></td>
        </tr>
        <tr>
            <td colspan="3">
                <div id="details-{i}" class="test-details">
                    <pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>
                </div>
            </td>
        </tr>
"""
    
    html += """
        </tbody>
    </table>
    
    <script>
        function toggleDetails(id) {
            const element = document.getElementById(id);
            if (element.style.display === 'block') {
                element.style.display = 'none';
            } else {
                element.style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""
    
    # 出力ディレクトリの作成
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # HTMLファイルの書き込み
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTMLレポートを生成しました: {output_file}")


def main():
    """メイン関数"""
    args = parse_arguments()
    
    # レポートディレクトリの確認
    if not os.path.isdir(args.report_dir):
        print(f"エラー: レポートディレクトリ {args.report_dir} が見つかりません。", file=sys.stderr)
        return 1
    
    # サマリーファイルの検索
    summary_file = find_summary_file(args.report_dir)
    
    # レポートファイルの検索
    report_files = find_report_files(args.report_dir)
    if not report_files:
        print(f"エラー: レポートファイルが見つかりません。", file=sys.stderr)
        return 1
    
    # HTMLレポートの生成
    generate_html_report(summary_file, report_files, args.output, args.title)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
