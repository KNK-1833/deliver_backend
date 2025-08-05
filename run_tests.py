#!/usr/bin/env python
"""
バックエンドテスト実行スクリプト

使用方法:
  python run_tests.py                    # 全テスト実行
  python run_tests.py --verbose          # 詳細出力で実行
  python run_tests.py --coverage         # カバレッジ測定付きで実行
  python run_tests.py --module users     # 特定モジュールのテストのみ実行
"""

import os
import sys
import subprocess
import argparse


def main():
    parser = argparse.ArgumentParser(description='バックエンドテスト実行スクリプト')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細出力')
    parser.add_argument('--coverage', '-c', action='store_true', help='カバレッジ測定')
    parser.add_argument('--module', '-m', help='特定モジュールのテストのみ実行')
    parser.add_argument('--parallel', '-p', action='store_true', help='並列実行')
    
    args = parser.parse_args()
    
    # プロジェクトルートに移動
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # 仮想環境のアクティベート
    venv_python = os.path.join('.venv', 'bin', 'python')
    if not os.path.exists(venv_python):
        print("Error: 仮想環境が見つかりません。先に仮想環境をセットアップしてください。")
        sys.exit(1)
    
    # pytestコマンドを構築
    cmd = [venv_python, '-m', 'pytest']
    
    # オプション追加
    if args.verbose:
        cmd.append('-v')
    else:
        cmd.append('--tb=short')
    
    if args.parallel:
        cmd.extend(['-n', 'auto'])
    
    # カバレッジ測定
    if args.coverage:
        cmd.extend(['--cov=backend/apps', '--cov-report=html', '--cov-report=term'])
    
    # 特定モジュールのテスト
    if args.module:
        cmd.append(f'test/backend/test_{args.module}.py')
    else:
        cmd.append('test/backend/')
    
    print(f"実行コマンド: {' '.join(cmd)}")
    print("-" * 50)
    
    # テスト実行
    try:
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ 全てのテストが成功しました！")
            if args.coverage:
                print("📊 カバレッジレポートが htmlcov/index.html に生成されました。")
        else:
            print("\n" + "=" * 50)
            print("❌ テストに失敗しました。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ テストが中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ テスト実行中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()