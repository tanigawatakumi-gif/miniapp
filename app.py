import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# Gemini API クライアントの初期化 (GEMINI_API_KEY 環境変数を利用)
client = genai.Client()

SYSTEM_PROMPT = """GitHub（GitHub Repositories, GitHub Actions, GitHub Codespaces）および Render や Vercel 等のサーバーホスティング、LINEミニアプリ（LIFF）を連携させたモック開発を行いたいです。
まずは開発をスムーズに進めるための「前提条件」をあなたにインプットします。以下のシステム構成および開発の注意点をすべて記憶してください。

アプリの具体的な仕様・デザイン・メニュー構成については、後ほど追加で指示を入力します。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ 1. 開発環境・システム構成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
・作業・管理環境：GitHub / GitHub Codespaces / VS Code
・CI/CD・本番デプロイ：GitHub Actions / Webホスティング（Render, Vercel等）
・バックエンド：Python (Flask / gunicorn)
・フロントエンド：HTML5, JavaScript (LIFF SDK), Tailwind CSS
・連携チャネルID（LINEログイン側）：【ご自身のチャネルID】
・LIFF ID：【ご自身のLIFF ID】

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 2. 開発における重要ルール（絶対厳守）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
① iPhone 15（画面幅393px）でのブラウザ最適化
LINE内ブラウザで文字が勝手に改行されるのを防ぐため、タイトルやボタンテキストには clamp 関数や、white-space: nowrap; を持たせた no-break クラスを徹底的に仕込むこと。

② キャッシュ対策およびプレビュー表示対策
LINEアプリはキャッシュが非常に強力なため、コードの冒頭にキャッシュ無効化のメタタグ（Cache-Controlなど）を必ず含めること。また、ローカル開発時のプレビュー確認時に勝手にLINEログイン画面に飛ばされてエラーにならないよう、環境判定（localhost等）で挙動を自動切り替えするロジックをJSに仕込むこと。

③ GitHub連携
リポジトリ管理を意識し、環境変数は .env ファイルやホスティングサービスの Secrets 機能で管理できるよう構成すること。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

以下の要件に基づき、完全な動くコードを出力してください。テキストでの挨拶や解説は不要です。コードブロックのみを出力してください。
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-code', methods=['POST'])
def generate_code():
    data = request.get_json()
    user_requirement = data.get('requirement', '')

    if not user_requirement:
        return jsonify({'error': '仕様要件が空です'}), 400

    full_prompt = f"{SYSTEM_PROMPT}\n【アプリ要件】\n{user_requirement}"

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
        )
        generated_text = response.text if response.text else "コードを生成できませんでした。"
        return jsonify({'result': generated_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
