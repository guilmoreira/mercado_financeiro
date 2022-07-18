{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "name": "MF_functions.ipynb",
      "provenance": [],
      "authorship_tag": "ABX9TyMxfvIJq5KMg/YXMifpMJ1R",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/guilmoreira/mercado_financeiro/blob/main/MF_functions2.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 2,
      "metadata": {
        "id": "l3pd7Z9v6nR-"
      },
      "outputs": [],
      "source": [
        "#FUNÇÃO BASEADA NA BIBLIOTECA QUANTSTATS\n",
        "def dd_details(database):\n",
        "  import numpy as np\n",
        "  import pandas as pd\n",
        "\n",
        "#FUNÇÃO PROPRIA DE DRAWDOWN\n",
        "  def drawdown(database):\n",
        "    #Converte uma série de preços em drawdown\n",
        "    returns_t=pd.DataFrame(database.pct_change().iloc[1:])\n",
        "    wea_t=pd.DataFrame(1000*(1+returns_t).cumprod())\n",
        "    picos_t=pd.DataFrame(wea_t.cummax())\n",
        "    drawdown_t=pd.DataFrame((wea_t-picos_t)/picos_t)\n",
        "    return drawdown_t\n",
        "\n",
        "  drawdown_input = drawdown(database)\n",
        "\n",
        "  def remove_outliers(returns, quantile=.95):\n",
        "    \"\"\"Returns series of returns without the outliers\"\"\"\n",
        "    return returns[returns < returns.quantile(quantile)]\n",
        "\n",
        "  def _drawdown_details(drawdown_input):\n",
        "      # mark no drawdown\n",
        "      no_dd = drawdown_input == 0\n",
        "\n",
        "      # extract dd start dates\n",
        "      starts = ~no_dd & no_dd.shift(1)\n",
        "      starts = list(starts[starts].index)\n",
        "\n",
        "      # extract end dates\n",
        "      ends = no_dd & (~no_dd).shift(1)\n",
        "      ends = list(ends[ends].index)\n",
        "\n",
        "      # no drawdown :)\n",
        "      if not starts:\n",
        "          return pd.DataFrame(\n",
        "              index=[], columns=('start', 'valley', 'end', 'days',\n",
        "                                'max drawdown', '99% max drawdown'))\n",
        "\n",
        "      # drawdown series begins in a drawdown\n",
        "      if ends and starts[0] > ends[0]:\n",
        "          starts.insert(0, drawdown_input.index[0])\n",
        "\n",
        "      # series ends in a drawdown fill with last date\n",
        "      if not ends or starts[-1] > ends[-1]:\n",
        "          ends.append(drawdown_input.index[-1])\n",
        "\n",
        "      # build dataframe from results\n",
        "      data = []\n",
        "      for i, _ in enumerate(starts):\n",
        "          dd = drawdown_input[starts[i]:ends[i]]\n",
        "          clean_dd = -remove_outliers(-dd, .99)\n",
        "          data.append((starts[i], dd.idxmin(), ends[i],\n",
        "                      (ends[i] - starts[i]).days,\n",
        "                      dd.min() * 100, clean_dd.min() * 100))\n",
        "\n",
        "      df = pd.DataFrame(data=data,\n",
        "                        columns=('start', 'valley', 'end', 'days',\n",
        "                                  'max drawdown',\n",
        "                                  '99% max drawdown'))\n",
        "      df['days'] = df['days'].astype(int)\n",
        "      df['max drawdown'] = df['max drawdown'].astype(float)\n",
        "      df['99% max drawdown'] = df['99% max drawdown'].astype(float)\n",
        "\n",
        "      df['start'] = df['start'].dt.strftime('%Y-%m-%d')\n",
        "      df['end'] = df['end'].dt.strftime('%Y-%m-%d')\n",
        "      df['valley'] = df['valley'].dt.strftime('%Y-%m-%d')\n",
        "      \n",
        "      return df\n",
        "      \n",
        "  if isinstance(drawdown_input, pd.DataFrame):\n",
        "      _dfs = {}\n",
        "      for col in drawdown_input.columns:\n",
        "          _dfs[col] = _drawdown_details(drawdown_input[col])\n",
        "      return pd.concat(_dfs, axis=1)\n",
        "  \n",
        "  return _drawdown_details(drawdown_input)"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "def drawdown(database):\n",
        "  #Converte uma série de preços em drawdown\n",
        "  returns_t=pd.DataFrame(database.pct_change().iloc[1:])\n",
        "  wea_t=pd.DataFrame(1000*(1+returns_t).cumprod())\n",
        "  picos_t=pd.DataFrame(wea_t.cummax())\n",
        "  drawdown_t=pd.DataFrame((wea_t-picos_t)/picos_t)\n",
        "  return drawdown_t"
      ],
      "metadata": {
        "id": "te3W1SXc7ArG"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "def dd_exporter(database,nome):\n",
        "  df=dd_details(database)\n",
        "  df.columns = ['start', 'valley', 'end', 'days','max drawdown','99% max drawdown']\n",
        "  df.sort_values(by=('max drawdown'),ascending=True, inplace=True)\n",
        "  rank=list(range(1,len(df)+1))\n",
        "  df['Rank']=rank\n",
        "  df.set_index('Rank',inplace=True)\n",
        "  df.to_excel(f'{nome}.xlsx')\n",
        "  return df"
      ],
      "metadata": {
        "id": "a2lkc5Qy7MIt"
      },
      "execution_count": 3,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        ""
      ],
      "metadata": {
        "id": "6_w2kBe87PHs"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}