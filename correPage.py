import io
import zipfile
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import os
import pandas as pd
from correlation import analyze_texts_in_directory
import plotly.express as px
import tempfile
import shutil
import base64

# __order__ = 3
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


KeyScanner = get_image_base64("KeyScanner.png")

# 初始化颜色配置
PRIMARY_COLOR = "#3f51b5"
SECONDARY_COLOR = "#5c6bc0"
ACCENT_COLOR = "#ff4081"
BG_COLOR = "#f8f9fa"
TEXT_COLOR = "#263238"


# 辅助函数（需在代码顶部定义）
def create_zip(temp_dir, file_list, folder_name):
    target_dir = os.path.join(temp_dir, folder_name)
    os.makedirs(target_dir, exist_ok=True)

    for entry in file_list:
        filename = entry[0] if isinstance(entry, tuple) else entry
        shutil.copy(os.path.join(temp_dir, filename),
                    os.path.join(target_dir, filename))

    zip_path = os.path.join(temp_dir, f"{folder_name}.zip")
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', target_dir)

    with open(zip_path, "rb") as f:
        return f.read()


# 初始化全局样式
def apply_custom_styles():
    st.markdown(f"""
    <style>
    /* 基础样式 */
    .stApp {{
        background-color: {BG_COLOR};
    }}

    /* 主标题样式 */
    .main-title {{
        font-size: 2.5rem;
        color: {PRIMARY_COLOR};
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
        letter-spacing: 1px;
    }}

    /* 分区标题样式 */
    .section-title {{
        font-size: 1.4rem;
        color: {TEXT_COLOR};
        padding: 0.8rem 1.2rem;
        background: linear-gradient(90deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
        color: white;
        border-radius: 8px;
        margin: 2rem 0 1.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    /* 统计卡片样式 */
    .stat-card {{
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 4px solid {PRIMARY_COLOR};
        transition: transform 0.2s;
    }}
    .stat-card:hover {{
        transform: translateY(-3px);
    }}

    /* 文件卡片样式 */
    .file-card {{
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid {PRIMARY_COLOR};
    }}

    /* 按钮样式 */
    .stButton>button {{
        background: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        border: none;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        background: {SECONDARY_COLOR};
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(63,81,181,0.2);
    }}

    /* 进度条样式 */
    .stProgress>div>div>div {{
        background: {PRIMARY_COLOR};
    }}

    /* 表格样式 */
    .stDataFrame {{
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    </style>
    """, unsafe_allow_html=True)


# 初始化 session state
if 'china_results' not in st.session_state:
    st.session_state.china_results = None


def app():
    apply_custom_styles()  # 应用自定义样式

    # 初始化 session state
    if "temp_dir" not in st.session_state:
        st.session_state.temp_dir = tempfile.mkdtemp()
    if "uploader_key_counter" not in st.session_state:
        st.session_state.uploader_key_counter = 0

    # 页面标题
    KeyScanner = get_image_base64("KeyScanner.png")

    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&family=Noto+Sans+SC:wght@400;700&display=swap');
            .title-container {{
                text-align: center;
                margin: 0 auto 2rem;
                max-width: 800px;
                padding: 1.5rem;
                border-radius: 12px;
                background: #f8f9fa;
            }}
            .title-with-logo {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
                margin-bottom: 0.5rem;
            }}
            .main-title {{
                font-family: 'Noto Sans SC', sans-serif;
                font-size: 2.2rem;
                color: #263238;
                letter-spacing: 1px;
                margin: 0;
            }}
            .logo-img {{
                width: 50px;
                height: 50px;
                object-fit: contain;
            }}
            .sub-title {{
                font-family: 'Roboto', sans-serif;
                font-size: 2rem;
                margin: 0.5rem 0;
                font-weight: 700;
                background: linear-gradient(90deg, #3f51b5, #5c6bc0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .description {{
                font-family: 'Noto Sans SC', sans-serif;
                text-align: center;
                color: #666;
                transform: translateX(100px);
                margin: 1.5rem auto;
                max-width: 600px;
                line-height: 1.7;
                font-size: 1.1rem;
                padding: 0 1rem;
            }}
        </style>

        <div class="title-container">
            <div class="title-with-logo">
                <img src="data:image/png;base64,{KeyScanner}" class="logo-img">
                <h1 class="main-title">提取核心声量</h1>
            </div>
            <h2 class="sub-title">KeyScanner</h2>
            <p class="description">
               基于于高频关键词和聚类分析的文本过滤引擎，自动清洗无关文本，精准锁定中国声音核心语料。
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    # 文件上传区域
    with st.container():
        st.markdown(f'<div class="section-title">📤 数据上传</div>', unsafe_allow_html=True)

        # 使用CSS样式定义上传区域
        st.markdown("""
        <style>
            .upload-area {
                border: 2px dashed #3f51b5;
                border-radius: 5px;
                padding: 20px;
                text-align: center;
                background-color: rgba(63,81,181,0.05);
                margin-bottom: 10px;
                transition: border-color 0.3s;
            }
            .upload-area:hover {
                border-color: #0068c9;
            }
            .upload-instruction {
                text-align: center;
                margin: 1em 0;
                color: #666;
            }
        </style>
        """, unsafe_allow_html=True)
        # 上传区域容器
        st.markdown("""
        <div class="upload-area">
                    <p style="text-align: center; margin: 1em 0; color: #666;">
                        ↓ 点击或拖拽文件到下方区域 ↓
                    </p>
        """, unsafe_allow_html=True)
        # 文件上传组件
        current_uploader_key = f"file_uploader_{st.session_state.uploader_key_counter}"
        uploaded_files = st.file_uploader(
            "",  # 空标签因为已经有视觉提示
            type=["txt", "zip"],
            accept_multiple_files=True,
            key=current_uploader_key,
            label_visibility="collapsed",  # 隐藏默认标签
            help="支持同时上传多个文件或包含多个文件的ZIP压缩包"
        )

        # 操作按钮组
        # 添加 CSS 样式调整按钮高度和列布局
        st.markdown("""
        <style>
        /* 调整按钮高度和边距 */
        .stButton > button {
            height: 100% !important;
            min-height: 55px;      /* 最小高度 */
            padding-top: 12px !important;
            padding-bottom: 12px !important;
        }
        /* 强制列高度对齐 */
        [data-testid="column"] {
            align-self: stretch !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # 创建宽度比例为 4:1 的列（根据需求调整比例）
        col1, col2 = st.columns([4, 1.2], gap="small")

        with col1:
            status_msg = uploaded_files and f"✅ 已成功上传 {len(uploaded_files)} 个文件" or "📤 等待文件上传..."
            st.info(status_msg)

        with col2:
            # 添加 use_container_width 让按钮填满列宽
            if st.button("🗑️ 清空缓存",
                         disabled=not uploaded_files,
                         use_container_width=True):
                st.session_state.uploader_key_counter += 1
                shutil.rmtree(st.session_state.temp_dir, ignore_errors=True)
                st.session_state.temp_dir = tempfile.mkdtemp()
                if "china_results" in st.session_state:
                    del st.session_state.china_results
                st.rerun()

    # 如果存在上传文件才显示后续内容
    if uploaded_files:
        # 保存文件到临时目录
        temp_dir = st.session_state.temp_dir
        for file in uploaded_files:
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            # 处理ZIP文件
            if file.name.lower().endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                os.remove(file_path)

        # 分析按钮
        if st.button("🔍 开始智能分析", type="primary", use_container_width=True):
            with st.spinner("正在进行深度文本分析..."):
                results = analyze_texts_in_directory(temp_dir)
                st.session_state.china_results = results
                st.toast("分析完成!", icon="✅")

        # 显示分析结果
        if st.session_state.get('china_results'):
            results = st.session_state.china_results

            # 仪表盘标题 - 扁平化设计
            st.markdown("""
            <div style="background-color: #3f51b5; color: white; padding: 12px 16px; 
                        border-radius: 8px; margin: 24px 0 16px 0; font-size: 1.2rem;">
                📊 分析仪表盘
            </div>
            """, unsafe_allow_html=True)

            total_files = len(results['related']) + len(results['not_related'])
            qualified_count = len(results['related'])
            unqualified_count = len(results['not_related'])

            # 扁平化统计卡片组
            metric_cols = st.columns(3)
            metric_style = """
                background: white; border-radius: 8px; padding: 16px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 16px;
            """

            with metric_cols[0]:
                st.markdown(f"""
                <div style="{metric_style} border-top: 4px solid #3f51b5;">
                    <div style="color: #666; font-size: 0.9rem;">总文本数</div>
                    <div style="font-size: 1.8rem; color: #3f51b5; font-weight: 600;">{total_files}</div>
                </div>
                """, unsafe_allow_html=True)

            with metric_cols[1]:
                st.markdown(f"""
                <div style="{metric_style} border-top: 4px solid #727dc4;">
                    <div style="color: #666; font-size: 0.9rem;">达标文本</div>
                    <div style="font-size: 1.8rem; color: #727dc4; font-weight: 600;">
                        {qualified_count} <span style="font-size: 1rem;">({(qualified_count / total_files * 100):.1f}%)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with metric_cols[2]:
                st.markdown(f"""
                <div style="{metric_style} border-top: 4px solid #b6bcdf;">
                    <div style="color: #666; font-size: 0.9rem;">不达标文本</div>
                    <div style="font-size: 1.8rem; color: #b6bcdf; font-weight: 600;">
                        {unqualified_count} <span style="font-size: 1rem;">({(unqualified_count / total_files * 100):.1f}%)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 数据可视化部分
            viz_cols = st.columns(2, gap="large")

            with viz_cols[0]:
                # 扁平化柱状图
                fig_bar = px.bar(
                    pd.DataFrame({
                        "类型": ["达标文本", "不达标文本"],
                        "数量": [qualified_count, unqualified_count]
                    }),
                    x="类型",
                    y="数量",
                    color="类型",
                    color_discrete_map={
                        "达标文本": "#727dc4",
                        "不达标文本": "#b6bcdf"
                    },
                    text="数量"
                )

                fig_bar.update_layout(
                    title="📈 文本分布",
                    title_font_size=16,
                    title_x=0.5,
                    showlegend=False,
                    height=330,
                    margin=dict(t=40, b=20, l=20, r=20),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#333"),
                    xaxis=dict(
                        gridcolor="#eee",
                        linecolor="#ddd"
                    ),
                    yaxis=dict(
                        gridcolor="#eee",
                        linecolor="#ddd"
                    )
                )

                fig_bar.update_traces(
                    textfont_size=12,
                    textposition="outside",
                    marker_line_width=0,
                    width=0.6
                )

                st.plotly_chart(fig_bar, use_container_width=True)

            with viz_cols[1]:
                # 扁平化饼图
                fig_pie = px.pie(
                    pd.DataFrame({
                        "类型": ["达标文本", "不达标文本"],
                        "数量": [qualified_count, unqualified_count]
                    }),
                    values="数量",
                    names="类型",
                    color="类型",
                    color_discrete_map={
                        "达标文本": "#727dc4",
                        "不达标文本": "#b6bcdf"
                    },
                    hole=0.4
                )

                fig_pie.update_layout(
                    title="📊 文本占比",
                    title_font_size=16,
                    title_x=0.5,
                    height=320,
                    margin=dict(t=40, b=20, l=20, r=20),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#333"),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    )
                )

                fig_pie.update_traces(
                    textinfo="percent+label",
                    textfont_size=12,
                    marker=dict(line=dict(color="white", width=1))
                )

                st.plotly_chart(fig_pie, use_container_width=True)
            # 聚类分析可视化部分
            st.markdown("---")  # 分割线保持简洁

            # 使用卡片式标题
            st.markdown("""
            <div style="background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%); 
                        color: white; padding: 12px 16px; border-radius: 8px; 
                        margin: 24px 0 16px 0; font-size: 1.2rem;">
                🧩 聚类分析可视化
            </div>
            """, unsafe_allow_html=True)

            # 创建两列布局
            col_cluster1, col_cluster2 = st.columns([1, 1], gap="large")

            with col_cluster1:
                # 树状图卡片
                st.markdown("""
                <div style="background: white; border-radius: 8px; padding: 5px; 
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 5px;">
                    <h3 style="text-align: center; color: #3f51b5; margin-bottom: 5px;">
                        🔍 聚类分布树状图
                    </h3>
                """, unsafe_allow_html=True)

                # 准备树状图数据
                cluster_data = []
                for cluster_id in set(cluster for _, cluster in results['clusters']):
                    cluster_files = [f for f, c in results['clusters'] if c == cluster_id]
                    qualified = sum(1 for f in cluster_files if f in results['related'])

                    cluster_data.append({
                        '聚类ID': f'聚类 {cluster_id}',
                        '总数': len(cluster_files),
                        '达标数': qualified,
                        '不达标数': len(cluster_files) - qualified,
                        '父级': '所有文档'
                    })

                cluster_df = pd.DataFrame(cluster_data)

                # 优化后的树状图
                fig_treemap = px.treemap(
                    cluster_df,
                    path=['父级', '聚类ID'],
                    values='总数',
                    color='聚类ID',
                    color_discrete_sequence=[f"rgba(63, 81, 181, {0.2 + 0.7 * i / len(cluster_data)})"
                                             for i in range(len(cluster_data))],
                    height=365,
                )

                # 扁平化样式调整
                fig_treemap.update_layout(
                    margin=dict(t=20, l=0, r=0, b=20),
                    uniformtext=dict(minsize=12, mode='hide'),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )

                fig_treemap.update_traces(
                    hovertemplate=None,  # 禁用悬停信息
                    hoverinfo='skip',  # 完全跳过悬停交互
                    textinfo="label+value",
                    textfont=dict(size=12, color="#333"),
                    marker=dict(line=dict(width=1, color='white')),
                    branchvalues='total'
                )

                st.plotly_chart(fig_treemap, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)  # 关闭卡片

            with col_cluster2:
                # 散点图卡片 - 优化间距版本
                st.markdown("""
                <div style="background: white; border-radius: 8px; padding: 5px; 
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
                            margin-bottom: 30px;
                            height: auto;  /* 改为自动高度 */
                            min-height: 700px;">
                    <div style="margin-bottom: 18px;">  <!-- 增加标题下方间距 -->
                        <h3 style="text-align: center; color: #3f51b5; 
                                   margin: 0; padding: 5px;">
                            📊 文档聚类分布
                        </h3>
                    </div>
                """, unsafe_allow_html=True)

                if 'clusters' in results and 'reduced_features' in results:
                    # 设置现代matplotlib样式
                    plt.style.use('seaborn-v0_8')
                    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] # mac电脑特别字体修改

                    # 创建图形（调整尺寸适应容器）
                    fig, ax = plt.subplots(figsize=(9, 6))  # 调整为更合理的比例
                    fig.patch.set_facecolor('white')
                    ax.set_facecolor('#f8f9fa')

                    # 准备数据
                    filenames = [f for f, _ in results['clusters']]
                    clusters = [c for _, c in results['clusters']]
                    reduced_features = np.array(results['reduced_features'])
                    related_files = [f for f, _ in results['related']]

                    # 颜色方案（使用蓝色系）
                    base_color = np.array([63, 81, 181]) / 255
                    cluster_colors = [
                        base_color * (0.6 + 0.4 * (i % 3))
                        for i in range(len(set(clusters)))
                    ]

                    # 绘制散点图
                    for cluster_id in sorted(set(clusters)):
                        mask = np.array([c == cluster_id for c in clusters])
                        points = reduced_features[mask]
                        is_qualified = np.array([
                            f in related_files for f in np.array(filenames)[mask]
                        ])

                        # 使用不同标记形状区分状态
                        ax.scatter(
                            points[is_qualified, 0], points[is_qualified, 1],
                            color=cluster_colors[cluster_id],
                            marker='o', s=72, alpha=0.85,
                            edgecolors='white', linewidth=0.8,
                            label=f'聚类{cluster_id} 达标'
                        )
                        ax.scatter(
                            points[~is_qualified, 0], points[~is_qualified, 1],
                            color=cluster_colors[cluster_id],
                            marker='s', s=72, alpha=0.85,
                            edgecolors='white', linewidth=0.8,
                            label=f'聚类{cluster_id} 待优化'
                        )

                    # 智能标注（根据密度自动选择）
                    from adjustText import adjust_text
                    texts = []
                    for i, (x, y) in enumerate(reduced_features[:15]):  # 只标注部分点
                        if np.random.random() < 0.3:  # 30%概率标注
                            texts.append(ax.text(
                                x, y, filenames[i],
                                fontsize=8, alpha=0.8,
                                bbox=dict(
                                    boxstyle='round,pad=0.3',
                                    fc='white', ec='none',
                                    alpha=0.7
                                )
                            ))
                    if texts:
                        adjust_text(texts,
                                    arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))

                    # 坐标轴样式
                    ax.set_xlabel('主成分1', fontsize=11, color='#555', labelpad=10)
                    ax.set_ylabel('主成分2', fontsize=11, color='#555', labelpad=10)

                    # 边框和网格
                    for spine in ['top', 'right']:
                        ax.spines[spine].set_visible(False)
                    for spine in ['left', 'bottom']:
                        ax.spines[spine].set_color('#ddd')

                    ax.grid(True, color='#eee', linestyle='-', linewidth=0.6)
                    ax.tick_params(axis='both', colors='#777', labelsize=10)

                    # 图例优化
                    handles, labels = ax.get_legend_handles_labels()
                    legend = ax.legend(
                        handles, labels,
                        loc='upper right',
                        bbox_to_anchor=(1.25, 1),
                        frameon=True,
                        framealpha=0.92,
                        facecolor='white',
                        edgecolor='#ddd',
                        title='图例',
                        title_fontsize=10,
                        fontsize=9,
                        borderaxespad=0.5
                    )
                    legend.get_title().set_fontweight('semibold')

                    # 增加图形底部间距
                    plt.tight_layout(pad=2.5)
                    st.pyplot(fig, bbox_inches='tight', pad_inches=0.5)

                st.markdown("</div>", unsafe_allow_html=True)  # 关闭卡片
            # 聚类详情表格 - 扁平化优化
            st.markdown("""
            <div style="background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%);
                        color: white; padding: 12px 16px; border-radius: 8px;
                        margin: 24px 0 16px 0; font-size: 1.2rem;">
                📋 聚类详情
            </div>
            """, unsafe_allow_html=True)

            # 准备表格数据（修复状态显示）
            cluster_details = []
            for filename, cluster in results['clusters']:
                status = "✅ 达标" if filename in [f for f, _ in results['related']] else "❌ 不达标"
                cluster_details.append({
                    '文件名': filename,
                    '所属聚类': f'聚类 {cluster}',
                    '状态': status
                })

            # 显示优化后的表格
            df_cluster = pd.DataFrame(cluster_details)
            st.markdown("""
            <style>
                .stDataFrame {
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }
                .stDataFrame th {
                    background-color: #f5f5f5 !important;
                }
                .stDataFrame tr:hover {
                    background-color: #f0f4ff !important;
                }
            </style>
            """, unsafe_allow_html=True)

            st.dataframe(
                df_cluster,
                column_config={
                    "文件名": st.column_config.Column(
                        width="large",
                        help="文档名称",
                        disabled=True
                    ),
                    "所属聚类": st.column_config.Column(
                        width="medium",
                        help="自动聚类结果",
                        disabled=True
                    ),
                    "状态": st.column_config.Column(
                        width="small",
                        help="检测状态",
                        disabled=True
                    )
                },
                height=min(400, 35 * len(df_cluster) + 40),  # 动态高度
                hide_index=True,
                use_container_width=True
            )
            # 添加悬停效果CSS
            st.markdown("""
            <style>
                .stDataFrame {
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                }
                .stDataFrame th {
                    background-color: #f5f5f5 !important;
                }
                .stDataFrame tr:hover {
                    background-color: #f0f4ff !important;
                }
                /* 状态列特殊样式 */
                [data-testid="stDataFrame"] td:nth-child(3) {
                    font-weight: 500 !important;
                    text-align: center !important;
                }
                [data-testid="stDataFrame"] td:nth-child(3):contains("✅") {
                    color: #4CAF50 !important;
                }
                [data-testid="stDataFrame"] td:nth-child(3):contains("❌") {
                    color: #F44336 !important;
                }
            </style>
            """, unsafe_allow_html=True)

            # 下载区域 - 蓝色渐变色系优化
            st.markdown("""
            <div style="background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%);
                        color: white; padding: 12px 16px; border-radius: 8px;
                        margin: 24px 0 16px 0; font-size: 1.2rem;">
                📥 检测结果导出
            </div>
            """, unsafe_allow_html=True)

            # 颜色定义
            BLUE_PRIMARY = "#3f51b5"
            BLUE_SECONDARY = "#5c6bc0"
            BLUE_VALID = "#6f77b6"  # 深蓝表示合格
            BLUE_INVALID = "#b6bcdf"  # 浅蓝表示不合格
            BLUE_LIGHT = "#e8f0fe"  # 背景浅蓝

            # 统计卡片
            col1, col2 = st.columns(2, gap="large")
            with col1:
                st.markdown(f"""
                <div style="background: white; border-radius: 8px; padding: 16px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
                            border-left: 4px solid {BLUE_VALID};
                            transition: transform 0.3s ease;">
                    <div style="font-size: 1rem; color: #5f6368;">达标文本</div>
                    <div style="font-size: 1.8rem; color: {BLUE_VALID}; font-weight: 600;">
                        {qualified_count} <span style="font-size: 1rem; color: #80868b;">个</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #80868b;">
                        <span style="color: {BLUE_VALID}; font-weight:500;">
                        {(qualified_count / total_files * 100):.1f}%</span> 占比
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="background: white; border-radius: 8px; padding: 16px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                            border-left: 4px solid {BLUE_INVALID};
                            transition: transform 0.3s ease;">
                    <div style="font-size: 1rem; color: #5f6368;">不达标文本</div>
                    <div style="font-size: 1.8rem; color: {BLUE_INVALID}; font-weight: 600;">
                        {unqualified_count} <span style="font-size: 1rem; color: #80868b;">个</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #80868b;">
                        <span style="color: {BLUE_INVALID}; font-weight:500;">
                        {(unqualified_count / total_files * 100):.1f}%</span> 占比
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 下载按钮组
            st.markdown("<br>", unsafe_allow_html=True)  # 增加间距
            dl_col1, dl_col2 = st.columns(2, gap="large")

            # 按钮样式定制
            st.markdown(f"""
            <style>
                /* 主按钮样式 */
                .stDownloadButton>button {{
                    background: {BLUE_VALID} !important;
                    color: white !important;
                    border: none !important;
                    transition: all 0.3s !important;
                }}
                .stDownloadButton>button:hover {{
                    background: {BLUE_PRIMARY} !important;
                    transform: translateY(-2px) !important;
                    box-shadow: 0 4px 8px rgba(63,81,181,0.2) !important;
                }}

                /* 次要按钮样式 */
                div[data-testid="stDownloadButton"]:nth-child(2)>button {{
                    background: {BLUE_INVALID} !important;
                }}
                div[data-testid="stDownloadButton"]:nth-child(2)>button:hover {{
                    background: #5c6bc0 !important;
                }}
            </style>
            """, unsafe_allow_html=True)
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                for filename in os.listdir(temp_dir):
                    zipf.write(os.path.join(temp_dir, filename), filename)
            st.session_state.qualified_zip = zip_buffer.getvalue()

            with dl_col1:
                if st.session_state.china_results['related']:
                    st.download_button(
                        label="⬇️ 导出达标文本",
                        data=create_zip(temp_dir, st.session_state.china_results['related'], "qualified"),
                        file_name="达标文本.zip",
                        help="下载所有符合标准的文本文件",
                        use_container_width=True,
                        key="dl_qualified"
                    )

                else:
                    st.warning("暂无达标文本可导出", icon="📭")

            with dl_col2:
                if st.session_state.china_results['not_related']:
                    st.download_button(
                        label="⬇️ 导出不达标文本",
                        data=create_zip(temp_dir, st.session_state.china_results['not_related'], "unqualified"),
                        file_name="不达标文本.zip",
                        help="下载所有需要优化的文本文件",
                        use_container_width=True,
                        key="dl_unqualified"
                    )
                else:
                    st.info("无待优化文本", icon="📭")

            # 文本详情展示 - 扁平化优化
            st.markdown("""
            <div style="background: linear-gradient(90deg, #3f51b5 0%, #5c6bc0 100%);
                        color: white; padding: 12px 16px; border-radius: 8px;
                        margin: 24px 0 16px 0; font-size: 1.2rem;">
                📄 文本详情分析
            </div>
            """, unsafe_allow_html=True)

            # 自定义标签页样式
            st.markdown("""
            <style>
                .stTabs [data-baseweb="tab-list"] {
                    gap: 10px;
                }
                .stTabs [data-baseweb="tab"] {
                    height: 40px;
                    padding: 0 20px;
                    border-radius: 8px 8px 0 0 !important;
                    background-color: #F0F2F6 !important;
                    transition: all 0.3s;
                }
                .stTabs [aria-selected="true"] {
                    background-color: #3f51b5 !important;
                    color: white !important;
                }
                .stTabs [data-baseweb="tab-highlight"] {
                    background-color: transparent !important;
                }
                .custom-expander {
                    border: 1px solid #e0e0e0 !important;
                    border-radius: 8px !important;
                    margin-bottom: 12px !important;
                }
                .custom-expander:hover {
                    box-shadow: 0 2px 8px rgba(63, 81, 181, 0.1) !important;
                }
            </style>
            """, unsafe_allow_html=True)

            # 创建标签页
            tab_labels = [
                f"达标文本 ({qualified_count}个)",
                f"不达标文本 ({unqualified_count}个)"
            ]
            tab1, tab2 = st.tabs(tab_labels)

            with tab1:
                if st.session_state.china_results['related']:
                    for file, details in st.session_state.china_results['related']:
                        with st.expander(f"📝 {file}", expanded=False):
                            cols = st.columns([1, 2], gap="medium")

                            # 检测结果面板
                            with cols[0]:
                                st.markdown("""
                                <div style="font-size: 1rem; color: #3f51b5; 
                                            margin-bottom: 8px; font-weight: 600;">
                                    🔍 检测结果
                                </div>
                                """, unsafe_allow_html=True)
                                st.code(details, language="json", line_numbers=True)

                            # 文件内容面板
                            with cols[1]:
                                st.markdown("""
                                <div style="font-size: 1rem; color: #3f51b5;
                                            margin-bottom: 8px; font-weight: 600;">
                                    📜 文件内容
                                </div>
                                """, unsafe_allow_html=True)
                                file_path = os.path.join(temp_dir, file)
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        st.text_area(
                                            label="content",
                                            value=content,
                                            height=200,
                                            label_visibility="collapsed",
                                            key=f"content_{file}",
                                        )
                                except Exception as e:
                                    st.error(f"文件读取错误: {str(e)}")
                else:
                    st.warning("未发现达标文本", icon="⚠️")

            with tab2:
                if st.session_state.china_results['not_related']:
                    for entry in st.session_state.china_results['not_related']:
                        filename = entry[0] if isinstance(entry, tuple) else entry

                        with st.expander(f"📝 {filename}", expanded=False):
                            file_path = os.path.join(temp_dir, filename)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()

                                    # 添加分析建议板块
                                    st.markdown("""
                                    <div style="font-size: 1rem; color: #f44336;
                                                margin-bottom: 8px; font-weight: 600;">
                                        ❗ 改进建议
                                    </div>
                                    <div style="background: #FFF3F3; padding: 12px; border-radius: 8px;
                                                margin-bottom: 16px; border-left: 4px solid #f44336;">
                                        建议检查文本与中国声音的关联性，参考关键词：政策、发展、文化等
                                    </div>
                                    """, unsafe_allow_html=True)

                                    st.text_area(
                                        label="file_content",
                                        value=content,
                                        height=200,
                                        label_visibility="collapsed",
                                        key=f"unqual_{filename}",
                                    )
                            except Exception as e:
                                st.error(f"文件读取错误: {str(e)}")
                else:
                    st.info("无不达标文本可分析", icon="ℹ️")

            # 添加全局悬浮效果
            st.markdown("""
            <style>
                div[data-testid="stExpander"]:hover {
                    border-color: #3f51b5 !important;
                }
                div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
                    gap: 0.5rem;
                }
            </style>
            """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        .footer {
            text-align: center;
            padding: 1.5rem 1rem;
            color: #555;
            border-top: 1px solid #eee;
            transition: all 0.3s;
        }
        .footer:hover {
            color: #333;
            background: #f9f9f9;
        }
    </style>

    <div class="footer">
        <p style="margin-bottom: 0.5rem;"><strong>© 2025 信源话语传播效果评估系统</strong></p>
        <div style="font-size: 0.9rem;">
            郇昌鹏 & 王玲玲｜研发
        </div>
        <div style="font-size: 0.75rem; margin-top: 0.8rem; color: #888;">
            版本号: V1.0 | 最后更新: 2025年4月
        </div>
    </div>
    """, unsafe_allow_html=True)
