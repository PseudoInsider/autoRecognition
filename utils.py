import base64
import numpy as np
import streamlit as st
import pandas as pd
import time

# __order__ = 5
# ---------------------- Image Handling ---------------------- #
def get_image_base64(path):
    """Converts an image file to a base64-encoded string."""
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Error: File '{path}' not found.")
        return None


def convert_image_to_bytes(image_path):
    """Converts an image file to bytes."""
    try:
        with open(image_path, "rb") as img_file:
            return img_file.read()
    except Exception as e:
        st.error(f"Error converting image to bytes: {e}")
        return None


# ---------------------- Session & Page Management ---------------------- #
def switch_page(page_name):
    """Switches the page using Streamlit session state."""
    st.session_state.current_page = page_name
    st.rerun()


def set_page_config(title="My Streamlit App", layout="wide", initial_sidebar_state="expanded"):
    """
    Sets the Streamlit page configuration.
    Call this at the very beginning of your app.
    """
    st.set_page_config(page_title=title, layout=layout, initial_sidebar_state=initial_sidebar_state)


# ---------------------- UI Enhancements ---------------------- #
def styled_card(title, subtitle, description, image_base64):
    """
    Generates an HTML card with an icon, title, and description.
    """
    return f"""
    <div class="card">
        <h3>
            <img src="data:image/png;base64,{image_base64}" 
            style="width:43px; height:40px; vertical-align:middle; margin-right:8px;">
            <span style="vertical-align:middle; color: #000000;">{title}</span>
        </h3>
        <h3>{subtitle}</h3>
        <p>{description}</p>
    </div>
    """


def apply_custom_css():
    """Injects custom CSS styles into the Streamlit app."""
    st.markdown("""
    <style>
        /* Main Container */
        .main { background-color: #f5f7fa; }

        /* Header */
        .header { background-color: #3f51b5; color: white; padding: 20px; border-radius: 0; margin-bottom: 30px; }

        /* Card Styling */
        .card { background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 25px; margin-bottom: 20px; transition: all 0.3s ease; border-left: 4px solid #3f51b5; }
        .card:hover { box-shadow: 0 5px 15px rgba(0,0,0,0.1); transform: translateY(-3px); }

        /* Buttons */
        .stButton>button { background-color: #3f51b5; color: white; border: none; border-radius: 4px; padding: 10px 24px; font-weight: 500; width: 100%; transition: all 0.3s; }
        .stButton>button:hover { background-color: #303f9f; transform: translateY(-2px); }

        /* Footer */
        .footer { text-align: center; padding: 1.5rem; margin-top: 3rem; color: #666; font-size: 0.9rem; border-top: 1px solid #eee; }

        /* Contact Form */
        .contact-form input, .contact-form textarea { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 4px; margin: 8px 0; font-size: 1rem; }
        .contact-form button { background-color: #3f51b5; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; margin-top: 8px; transition: all 0.3s; }
        .contact-form button:hover { background-color: #303f9f; }
    </style>
    """, unsafe_allow_html=True)


def contact_form(email="your@email.com"):
    """
    Generates an HTML contact form.
    """
    return f"""
    <div class="contact-form">
        <h4 style="color: #3f51b5;">技术合作与咨询</h4>
        <p>如有任何问题或合作意向，请联系研发团队：</p>
        <form action="https://formsubmit.co/{email}" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="text" name="name" placeholder="您的姓名" required>
            <input type="email" name="email" placeholder="您的邮箱" required>
            <textarea name="message" placeholder="您的留言"></textarea>
            <button type="submit">发送消息</button>
        </form>
    </div>
    """


# ---------------------- Data Handling ---------------------- #
def read_csv_file(file_path, encoding="utf-8"):
    """Reads a CSV file and returns a pandas DataFrame."""
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        return df
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None


def read_excel_file(file_path):
    """Reads an Excel file and returns a pandas DataFrame."""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return None


def generate_download_link(data, file_name="data.csv", file_label="Download CSV"):
    """
    Generates a download link for a given data (CSV format).
    """
    try:
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # Convert to base64
        href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}">{file_label}</a>'
        return href
    except Exception as e:
        st.error(f"Error generating download link: {e}")
        return None


# ---------------------- Caching & Performance ---------------------- #
def cache_function(func):
    """
    A decorator to cache expensive function results using Streamlit's caching.
    """
    return st.cache(func)


def measure_execution_time(func):
    """
    A decorator to measure the execution time of a function.
    Displays the elapsed time in the Streamlit app.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        st.write(f"Execution time: {elapsed_time:.4f} seconds")
        return result

    return wrapper


# ---------------------- Messaging & Notifications ---------------------- #
def show_info_message(message, title="Information"):
    """Displays a styled information message."""
    st.info(f"**{title}:** {message}")


def show_error_message(message, title="Error"):
    """Displays a styled error message."""
    st.error(f"**{title}:** {message}")


def show_success_message(message, title="Success"):
    """Displays a styled success message."""
    st.success(f"**{title}:** {message}")


def show_warning_message(message, title="Warning"):
    """Displays a styled warning message."""
    st.warning(f"**{title}:** {message}")


# ---------------------- User Authentication ---------------------- #
def login_form(validate_credentials_func):
    """
    Renders a login form and handles authentication.
    Args:
        validate_credentials_func (function): Function that takes (username, password)
                                              and returns True if valid
    """
    with st.form("Login"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submitted = st.form_submit_button("登录")

        if submitted:
            if validate_credentials_func(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("登录成功!")
                return True
            else:
                st.error("用户名或密码错误")
                return False
    return False


def logout_button():
    """Renders and handles logout functionality."""
    if st.button("退出登录"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success("已成功退出登录")
        st.rerun()


def protected_page():
    """Checks if user is logged in, redirects to login if not."""
    if not st.session_state.get("logged_in"):
        st.warning("请先登录以访问此页面")
        switch_page("login")
        return False
    return True


# ---------------------- Form Handling ---------------------- #
class MultiStepForm:
    """Handles multi-step form navigation and state management."""

    def __init__(self, steps):
        self.steps = steps
        if "form_step" not in st.session_state:
            st.session_state.form_step = 0

    def show(self):
        current_step = min(st.session_state.form_step, len(self.steps) - 1)
        self.steps[current_step]()

        col1, col2 = st.columns([1, 1])
        with col1:
            if current_step > 0:
                if st.button("上一步"):
                    st.session_state.form_step -= 1
                    st.rerun()
        with col2:
            if current_step < len(self.steps) - 1:
                if st.button("下一步"):
                    st.session_state.form_step += 1
                    st.rerun()
            else:
                if st.button("提交"):
                    st.session_state.form_step = 0
                    st.success("表单提交成功!")


# ---------------------- Data Visualization ---------------------- #
def styled_dataframe(df, highlight_max=True):
    """Displays a pandas DataFrame with enhanced styling."""
    style = df.style
    if highlight_max:
        style = style.highlight_max(color='#90EE90')
    st.markdown(style.to_html(), unsafe_allow_html=True)


def interactive_table(data, page_size=10):
    """Creates a paginated interactive table."""
    page = st.number_input("页码", min_value=1,
                           max_value=len(data) // page_size + 1, value=1)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    st.table(data.iloc[start_idx:end_idx])


# ---------------------- File Handling ---------------------- #
def handle_file_upload(accept_types=["csv", "xlsx"], max_size_mb=10):
    """Handles file upload with validation."""
    uploaded_file = st.file_uploader(
        "上传文件",
        type=accept_types,
        help=f"最大文件大小: {max_size_mb}MB"
    )

    if uploaded_file:
        # Check file size
        if uploaded_file.size > max_size_mb * 1024 * 1024:
            show_error_message(f"文件大小超过{max_size_mb}MB限制")
            return None

        # Read file content
        try:
            if uploaded_file.type == "text/csv":
                return pd.read_csv(uploaded_file)
            elif "spreadsheet" in uploaded_file.type:
                return pd.read_excel(uploaded_file)
            else:
                return uploaded_file.read()
        except Exception as e:
            show_error_message(f"文件读取失败: {str(e)}")
            return None
    return None


# ---------------------- Date/Time Handling ---------------------- #


# ---------------------- Input Validation ---------------------- #
def validate_email(email):
    """Validates email format using regex."""
    import re
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validates Chinese phone number format."""
    import re
    pattern = r"^1[3-9]\d{9}$"
    return re.match(pattern, phone) is not None


# ---------------------- Progress Tracking ---------------------- #
class ProgressTracker:
    """Tracks and displays progress of multi-step processes."""

    def __init__(self, steps):
        self.steps = steps
        self.current = 0

    def update(self):
        """Updates and displays current progress."""
        self.current += 1
        progress = self.current / len(self.steps)

        st.write(f"当前步骤: {self.steps[self.current - 1]}")
        st.progress(progress)

        if self.current == len(self.steps):
            st.balloons()
            self.reset()

    def reset(self):
        self.current = 0


# ---------------------- Error Handling ---------------------- #
def error_boundary(func):
    """Decorator for catching and displaying exceptions."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            show_error_message(f"操作失败: {str(e)}")
            st.error("""```
            {traceback.format_exc()}
            ```""")

    return wrapper


# ---------------------- Localization ---------------------- #
def localized_text(lang="cn"):
    """Provides localized text snippets."""
    translations = {
        "welcome": {
            "cn": "欢迎使用本系统",
            "en": "Welcome to the System"
        },
        "login": {
            "cn": "登录",
            "en": "Login"
        }
    }
    return translations.get(lang, translations["cn"])


def date_range_picker():
    """Creates a date range picker with presets."""

    today = pd.Timestamp.today()
    presets = {
        "最近7天": (today - pd.DateOffset(days=7), today),
        "本月": (today.replace(day=1), today),
        "今年": (today.replace(month=1, day=1), today)
    }

    col1, col2 = st.columns(2)
    with col1:
        preset = st.selectbox("快速选择", list(presets.keys()))

    with col2:
        start_date = st.date_input("开始日期", value=presets[preset][0])
    end_date = st.date_input("结束日期", value=presets[preset][1], max_value=today)

    return start_date, end_date

# ---------------------- SEO & Analytics ---------------------- #
def inject_google_analytics(ga_id):
    """Injects Google Analytics tracking code."""
    st.markdown(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}');
    </script>
    """, unsafe_allow_html=True)

# ---------------------- Advanced UI Components ---------------------- #
def toggle_theme_button():
    """Adds a theme toggle button (light/dark mode)"""
    if st.button("🌙" if st.get_theme().base == "light" else "☀️"):
        current_theme = st.get_theme()
        new_theme = {
            "base": "dark" if current_theme.base == "light" else "light",
            "primaryColor": current_theme.primaryColor,
            "backgroundColor": current_theme.backgroundColor,
            "secondaryBackgroundColor": current_theme.secondaryBackgroundColor,
            "textColor": current_theme.textColor,
            "font": current_theme.font
        }
        st.set_theme(new_theme)
        st.rerun()

def expandable_card(title, content, expanded=False):
    """Creates an expandable card component"""
    with st.expander(title, expanded=expanded):
        st.markdown(content)

def floating_action_button(text, icon="➕", on_click=None):
    """Creates a floating action button with custom styling"""
    st.markdown(f"""
    <style>
        .fab {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }}
    </style>
    <button class="fab" onclick="alert('Clicked!')">
        {icon} {text}
    </button>
    """, unsafe_allow_html=True)

    # ---------------------- Data Processing ---------------------- #
    def clean_dataframe(df, drop_na_threshold=0.7):
        """Automatically cleans a DataFrame with common operations"""
        # Drop columns with too many missing values
        df = df.dropna(axis=1, thresh=int(drop_na_threshold * len(df)))

        # Convert string numbers to numeric
        for col in df.select_dtypes(include=['object']):
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass

        # Convert date strings to datetime
        for col in df.select_dtypes(include=['object']):
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

        return df

def memory_optimize(df):
    """Reduces memory usage of a DataFrame"""
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    for col in df.columns:
        col_type = df[col].dtypes
        if col_type in numerics:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                else:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
    return df


# ---------------------- Performance Tools ---------------------- #
class PerformanceMonitor:
    """Context manager for measuring code block execution time"""

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.execution_time = self.end_time - self.start_time
        st.metric("Execution time", f"{self.execution_time:.4f} seconds")


def memory_usage_widget():
    """Displays current memory usage"""
    import psutil
    process = psutil.Process()
    mem = process.memory_info().rss / (1024 ** 2)  # in MB
    st.metric("Memory Usage", f"{mem:.2f} MB")


# ---------------------- Security Utilities ---------------------- #
def sanitize_input(input_str):
    """Basic input sanitization to prevent XSS"""
    import html
    return html.escape(input_str)


def password_strength_checker(password):
    """Checks password strength and provides feedback"""
    import re
    feedback = []

    if len(password) < 8:
        feedback.append("密码至少需要8个字符")
    if not re.search(r"[A-Z]", password):
        feedback.append("需要至少一个大写字母")
    if not re.search(r"[a-z]", password):
        feedback.append("需要至少一个小写字母")
    if not re.search(r"\d", password):
        feedback.append("需要至少一个数字")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        feedback.append("需要至少一个特殊字符")

    return feedback if feedback else ["密码强度足够"]


# ---------------------- Notification System ---------------------- #
def show_toast(message, duration=3, position="bottom-right"):
    """Displays a toast notification"""
    positions = {
        "top-right": "top: 20px; right: 20px;",
        "top-left": "top: 20px; left: 20px;",
        "bottom-right": "bottom: 20px; right: 20px;",
        "bottom-left": "bottom: 20px; left: 20px;"
    }

    st.markdown(f"""
    <style>
        .toast {{
            position: fixed;
            {positions.get(position, positions["bottom-right"])}
            background-color: #333;
            color: white;
            padding: 15px;
            border-radius: 5px;
            z-index: 1000;
            animation: fadein 0.5s, fadeout 0.5s {duration}s;
        }}
        @keyframes fadein {{
            from {{opacity: 0;}}
            to {{opacity: 1;}}
        }}
        @keyframes fadeout {{
            from {{opacity: 1;}}
            to {{opacity: 0;}}
        }}
    </style>
    <div class="toast">{message}</div>
    """, unsafe_allow_html=True)
    time.sleep(duration + 0.5)


# ---------------------- PDF Generation ---------------------- #
def generate_pdf(content, filename="report.pdf"):
    """Generates a PDF from HTML content"""
    from weasyprint import HTML
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        HTML(string=content).write_pdf(f.name)
        with open(f.name, "rb") as f:
            st.download_button(
                "下载PDF报告",
                f.read(),
                file_name=filename,
                mime="application/pdf"
            )


# ---------------------- System Utilities ---------------------- #
def get_system_info():
    """Displays system information"""
    import platform, socket, cpuinfo

    info = {
        "操作系统": platform.system(),
        "操作系统版本": platform.version(),
        "处理器": cpuinfo.get_cpu_info()['brand_raw'],
        "主机名": socket.gethostname(),
        "Python版本": platform.python_version(),
        "Streamlit版本": st.__version__,
        "Pandas版本": pd.__version__
    }

    st.table(pd.DataFrame.from_dict(info, orient="index", columns=["值"]))


# ---------------------- Experimental Features ---------------------- #
def typewriter_effect(text, speed=0.05):
    """Creates a typewriter effect for text display"""
    from streamlit.components.v1 import html

    html(f"""
    <div id="typewriter"></div>
    <script>
        var i = 0;
        var text = `{text}`;
        var speed = {speed * 1000};

        function typeWriter() {{
            if (i < text.length) {{
                document.getElementById("typewriter").innerHTML += text.charAt(i);
                i++;
                setTimeout(typeWriter, speed);
            }}
        }}
        typeWriter();
    </script>
    """)


def confetti_effect():
    """Triggers a confetti celebration effect"""
    st.markdown("""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <script>
        confetti({
            particleCount: 150,
            spread: 70,
            origin: { y: 0.6 }
        });
    </script>
    """, unsafe_allow_html=True)


# ---------------------- Enhanced Visualization ---------------------- #
def interactive_plot(df, x_col, y_cols, plot_type='line', height=400):
    """Creates an interactive plot with Plotly"""
    import plotly.express as px

    plot_types = {
        'line': px.line,
        'bar': px.bar,
        'scatter': px.scatter,
        'area': px.area,
        'histogram': px.histogram
    }

    fig = plot_types[plot_type](
        df,
        x=x_col,
        y=y_cols,
        title=f"{plot_type.capitalize()} Plot of {', '.join(y_cols)} vs {x_col}",
        height=height
    )

    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='LightGray')
    )

    st.plotly_chart(fig, use_container_width=True)


def correlation_matrix_heatmap(df, annot=True):
    """Displays a styled correlation matrix heatmap"""
    import seaborn as sns
    import matplotlib.pyplot as plt

    corr = df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr,
        mask=mask,
        annot=annot,
        cmap='coolwarm',
        center=0,
        fmt=".2f",
        linewidths=.5,
        ax=ax
    )
    plt.title('Correlation Matrix', fontsize=16)
    st.pyplot(fig)


def time_series_decomposition(df, date_col, value_col, period=12):
    """Decomposes time series data into trend/seasonal/residual components"""
    from statsmodels.tsa.seasonal import seasonal_decompose

    df = df.set_index(date_col)
    result = seasonal_decompose(df[value_col], model='additive', period=period)

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 8))
    result.observed.plot(ax=ax1, title='Observed')
    result.trend.plot(ax=ax2, title='Trend')
    result.seasonal.plot(ax=ax3, title='Seasonality')
    result.resid.plot(ax=ax4, title='Residuals')
    fig.tight_layout()
    st.pyplot(fig)


def sankey_diagram(labels, sources, targets, values):
    """Creates an interactive Sankey diagram"""
    import plotly.graph_objects as go

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values
        )
    ))

    fig.update_layout(title_text="Sankey Diagram", font_size=10)
    st.plotly_chart(fig, use_container_width=True)


def radar_chart(categories, values, title="Radar Chart"):
    """Creates a radar/spider chart"""
    import plotly.express as px

    fig = px.line_polar(
        r=values,
        theta=categories,
        line_close=True,
        title=title
    )
    fig.update_traces(fill='toself')
    st.plotly_chart(fig, use_container_width=True)


def gantt_chart(data, start_col, end_col, task_col, color_col=None):
    """Creates an interactive Gantt chart"""
    import plotly.express as px

    fig = px.timeline(
        data,
        x_start=start_col,
        x_end=end_col,
        y=task_col,
        color=color_col,
        title="Gantt Chart"
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

def chart_selector(df):
    """Interactive chart type selector with automatic axis detection"""
    col1, col2 = st.columns(2)

    with col1:
        chart_type = st.selectbox(
            "Chart Type",
            ["Line", "Bar", "Scatter", "Histogram", "Box Plot"]
        )

    with col2:
        x_axis = st.selectbox(
            "X-Axis",
            df.columns,
            index=0
        )

    y_axes = st.multiselect(
        "Y-Axes",
        df.select_dtypes(include=['number']).columns.tolist(),
        default=df.select_dtypes(include=['number']).columns.tolist()[:1]
    )

    if chart_type and x_axis and y_axes:
        interactive_plot(df, x_axis, y_axes, plot_type=chart_type.lower())


def create_dashboard_grid(plots, cols=2, height=300):
    """Organizes multiple plots in a responsive grid"""
    import math

    rows = math.ceil(len(plots) / cols)
    grid = [st.columns(cols) for _ in range(rows)]

    for idx, plot in enumerate(plots):
        row = idx // cols
        col = idx % cols
        with grid[row][col]:
            plot(height=height)


def small_multiple_charts(df, value_cols, n_cols=3, chart_type='line'):
    """Creates small multiples of the same chart type"""
    import plotly.express as px

    n_rows = (len(value_cols) + n_cols - 1) // n_cols
    fig = px.line(
        df.melt(id_vars=df.index.name),
        x=df.index.name,
        y='value',
        facet_col='variable',
        facet_col_wrap=n_cols,
        height=300 * n_rows
    )
    st.plotly_chart(fig, use_container_width=True)