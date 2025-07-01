import streamlit as st
import akshare as ak
import pandas as pd

st.set_page_config(page_title="A股格雷厄姆估值工具", layout="wide")
st.title("📈 A股格雷厄姆估值与选股助手")

stock_input = st.text_area("请输入股票代码（每行一个，例如：600519）", height=150)
if stock_input:
    stock_list = [code.strip() for code in stock_input.strip().splitlines() if code.strip()]
    result = []

    with st.spinner("正在分析..."):
        price_df = ak.stock_zh_a_spot_em()  # 获取全部A股实时数据

        for code in stock_list:
            try:
                df = ak.stock_financial_abstract(symbol=code)
                eps = float(df[df["指标名称"] == "基本每股收益(元)"].iloc[0]["2023年报"])
                growth_rate = float(df[df["指标名称"] == "归母净利润同比增长率"].iloc[0]["2023年报"])
                growth_rate = max(growth_rate, 0)

                price = float(price_df[price_df["代码"] == code].iloc[0]["最新价"])

                value = eps * (8.5 + 2 * growth_rate)
                margin = (value - price) / value
                peg = (price / eps) / growth_rate if growth_rate > 0 else None

                advice = "🟢 低估" if margin > 0.3 and peg and peg < 1 else "🟡 观察" if peg and peg < 1.5 else "🔴 高估"

                result.append({
                    "股票代码": code,
                    "EPS": eps,
                    "增长率%": growth_rate,
                    "当前股价": price,
                    "格雷厄姆估值": round(value, 2),
                    "安全边际%": round(margin * 100, 2),
                    "PEG": round(peg, 2) if peg else "N/A",
                    "建议": advice
                })

            except Exception as e:
                st.warning(f"{code} 获取失败：{e}")

    if result:
        df_out = pd.DataFrame(result)
        st.dataframe(df_out, use_container_width=True)

        st.download_button(
            label="📁 下载结果 Excel",
            data=df_out.to_excel(index=False),
            file_name="格雷厄姆估值选股结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )