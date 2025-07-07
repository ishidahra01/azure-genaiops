# GitHub Actions用 Azure Federated Credentials 設定手順

このドキュメントでは、GitHub ActionsからAzureリソースにアクセスするためのFederated Credentialsの設定方法を説明します。

## 前提条件

- Azureサブスクリプションへのアクセス権限
- GitHubリポジトリの管理者権限
- Azure CLI または Azure Portal へのアクセス

## 1. Azure側の設定

### 1.1 サービスプリンシパルの作成

#### Azure CLI を使用する場合

```bash
# Azure CLIにログイン
az login

# サービスプリンシパルを作成
az ad sp create-for-rbac --name "github-actions-azure-genaiops" --role contributor --scopes /subscriptions/{subscription-id}
```

#### Azure Portal を使用する場合

1. **Azure Portal** → **Azure Active Directory** → **App registrations**
2. **New registration** をクリック
3. アプリケーション名: `github-actions-azure-genaiops`
4. **Register** をクリック

### 1.2 必要な情報の取得

作成したアプリケーション（サービスプリンシパル）から以下の情報を取得：

```text
Application (client) ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Directory (tenant) ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Subscription ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 1.3 Federated Credentials の設定

1. **Azure Portal** → **Azure Active Directory** → **App registrations**
2. 作成したアプリケーションを選択
3. **Certificates & secrets** → **Federated credentials** → **Add credential**
4. 以下のように設定：

```text
Federated credential scenario: GitHub Actions deploying Azure resources
Organization: [あなたのGitHubユーザー名またはOrganization名]
Repository: azure-genaiops
Entity type: Branch
GitHub branch name: main
Name: github-actions-main-branch
Description: GitHub Actions from main branch
```

### 1.4 権限の設定

サービスプリンシパルに必要なAzureリソースへのアクセス権限を付与：

1. **Azure Portal** → **Subscriptions** → 対象のサブスクリプション
2. **Access control (IAM)** → **Add role assignment**
3. **Role**: `Contributor` または必要最小限の権限
4. **Assign access to**: User, group, or service principal
5. **Select**: 作成したサービスプリンシパル名を検索して選択

## 2. GitHub側の設定

### 2.1 Repository Variables の設定

1. GitHubリポジトリ (`azure-genaiops`) にアクセス
2. **Settings** タブをクリック
3. 左サイドバーで **Secrets and variables** → **Actions** をクリック
4. **Variables** タブを選択
5. **New repository variable** をクリックして以下を追加：

#### 必要な変数

```text
Name: AZURE_CLIENT_ID
Value: [1.2で取得したApplication (client) ID]

Name: AZURE_TENANT_ID
Value: [1.2で取得したDirectory (tenant) ID]

Name: AZURE_SUBSCRIPTION_ID
Value: [1.2で取得したSubscription ID]
```

## 3. ワークフローファイルの確認

`.github/workflows/ai-agent-evals.yml` ファイルが以下のようになっていることを確認：

```yaml
name: "AI Agent Evaluation"

on:
  workflow_dispatch:
  push:
    branches:
      - main

permissions:
  id-token: write
  contents: read

jobs:
  run-action:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Azure login using Federated Credentials
        uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

      - name: Run Evaluation
        uses: microsoft/ai-agent-evals@v2-beta
        with:
          azure-ai-project-endpoint: "https://agent-ai-servicesgkl4.services.ai.azure.com/api/projects/agent-ai-servicesgkl4-project"
          deployment-name: "gpt-4.1"
          agent-ids: "asst_ALYoZcjXx82cFGXMzlgwfh77"
          data-path: ${{ github.workspace }}/data/eval_data.jsonl
```

## 4. 動作確認

### 4.1 テスト実行

1. GitHubリポジトリで **Actions** タブをクリック
2. **AI Agent Evaluation** ワークフローを選択
3. **Run workflow** をクリックして手動実行
4. ログでAzureログインが成功することを確認

### 4.2 トラブルシューティング

#### よくあるエラーと対処法

**エラー**: `AADSTS70021: No matching federated identity record found`

- **原因**: Federated Credentialsの設定が間違っている
- **対処**: Organization名、Repository名、Branch名を再確認

**エラー**: `AADSTS50105: The signed in user is not assigned to a role`

- **原因**: サービスプリンシパルに適切な権限が付与されていない
- **対処**: Azure Portal でロールの割り当てを確認

**エラー**: `Repository variable not found`

- **原因**: GitHub Variables が正しく設定されていない
- **対処**: リポジトリの Settings → Secrets and variables → Actions で変数を確認

## 5. セキュリティのベストプラクティス

- **最小権限の原則**: 必要最小限の権限のみを付与
- **環境の分離**: 本番環境用には別のサービスプリンシパルを使用
- **定期的な監査**: アクセスログを定期的に確認
- **権限の見直し**: 不要になった権限は速やかに削除

## 参考リンク

- [GitHub Actions での OpenID Connect の使用](https://docs.github.com/ja/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [Azure での GitHub Actions の構成](https://docs.microsoft.com/ja-jp/azure/developer/github/connect-from-azure)
- [Azure Login Action](https://github.com/Azure/login)
