# Azure AI Evaluation Batch Processing

このプロジェクトは、Azure AI Evaluation SDKを使用してGenerative AIアプリケーションのバッチ評価を実行するためのツールです。

## 機能

- RAG（Retrieval Augmented Generation）評価
- 一般的な品質評価
- 安全性評価
- カスタム評価器のサポート
- CI/CD環境での自動実行

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`ファイルを参考に、必要な環境変数を設定してください。

```bash
cp .env.example .env
```

以下の環境変数が必要です：

- `AZURE_AI_PROJECT_ENDPOINT`: Azure AI Foundryプロジェクトのエンドポイント
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAIサービスのエンドポイント
- `AZURE_OPENAI_API_KEY`: Azure OpenAI APIキー
- `AZURE_OPENAI_CHAT_DEPLOYMENT`: チャット完了デプロイメント名
- `AZURE_OPENAI_API_VERSION`: Azure OpenAI APIバージョン
- `EVAL_DATA_PATH`: 評価データファイルのパス（オプション）
- `OUTPUT_PATH`: 結果出力パス（オプション）
- `LOG_LEVEL`: ログレベル（DEBUG, INFO, WARNING, ERROR）（オプション、デフォルト: INFO）
- `DEBUG_MODE`: デバッグモード（true/false）（オプション、デフォルト: false）

#### ログ制御について

デフォルトでは、Azure SDKやHTTPライブラリの詳細なAPIレスポンスヘッダー情報は抑制されています。

- **通常の実行**: `LOG_LEVEL=INFO`, `DEBUG_MODE=false` でクリーンなログ出力
- **デバッグ時**: `DEBUG_MODE=true` でより詳細な情報を表示
- **詳細ログ**: `LOG_LEVEL=DEBUG` で最も詳細なログを表示

### 3. 評価データの準備

評価データは以下の形式のJSONLファイルである必要があります：

```json
{
  "query": "ユーザーからの質問",
  "retrieved_results": "検索結果のコンテキスト",
  "response": "AIアプリケーションからの回答",
  "ground_truth": "正解となる回答"
}
```

## ローカル実行

```bash
cd apps
python 01_azure_ai_evaluation_batch.py
```

## GitHub Actionsでの実行

### 前提条件

GitHub Actionsで実行するには、以下のSecretsを設定する必要があります：

#### Azure認証用（OIDC認証推奨）

- `AZURE_CLIENT_ID`: Azure Active DirectoryアプリケーションのクライアントID
- `AZURE_TENANT_ID`: Azureテナントの ID
- `AZURE_SUBSCRIPTION_ID`: Azureサブスクリプション ID

#### Azure AI関連

- `AZURE_AI_PROJECT_ENDPOINT`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

### Azure OIDC認証の設定

GitHub ActionsでAzureリソースにアクセスするために、フェデレーテッド認証情報を設定することを推奨します。詳細は[setup-federated-credentials.md](docs/setup-federated-credentials.md)を参照してください。

### ワークフローの実行

ワークフローは以下のタイミングで自動実行されます：

- `main`または`develop`ブランチへのプッシュ
- `main`ブランチへのプルリクエスト
- 毎日午前2時（UTC）の定期実行
- 手動実行

## 評価器の種類

### RAG評価器

- **Retrieval**: 検索の有効性を測定
- **Response Completeness**: 回答の完全性を評価

### 一般評価器

- **QA**: 質問応答タスクの総合的な品質評価

### 安全性評価器

- **Content Safety**: コンテンツの安全性評価
- **Hate Unfairness**: ヘイトスピーチや不公平性の検出

## 結果の確認

### ローカル実行の場合

- コンソールに評価サマリーが表示されます
- `OUTPUT_PATH`で指定したパスに詳細結果がJSON形式で保存されます

### GitHub Actionsの場合

- プルリクエストに評価結果がコメントとして投稿されます
- Artifactsとして評価結果とログファイルがアップロードされます
- GitHub Actionsのサマリーページに結果が表示されます

## トラブルシューティング

### 認証エラー

- Azure認証情報が正しく設定されているか確認してください
- Managed Identityが適切な権限を持っているか確認してください

### データ形式エラー

- 評価データファイルが正しいJSONL形式になっているか確認してください
- 必須フィールド（query, retrieved_results, response, ground_truth）が含まれているか確認してください

### API制限エラー

- Azure OpenAIのレート制限に達していないか確認してください
- 必要に応じて`EVALUATION_THRESHOLD`を調整してください

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
