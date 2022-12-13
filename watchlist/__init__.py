import os
import sys

# SQLite URI compatible
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
# session 用来在请求间存储数据，它会把数据签名后存储到浏览器的 Cookie 中，所以我们需要设置签名所需的密钥：
# 这个密钥的值在开发时可以随便设置。基于安全的考虑，在部署时应该设置为随机字符，且不应该明文写在代码里
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
# 数据库文件一般放到项目根目录
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path),
                                                              os.getenv('DATABASE_FILE', 'data.db'))
# 关闭对模型修改的监控
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

# 实例化扩展类
login_manager = LoginManager(app)
# 如果未登录的用户访问对应的 URL，Flask-Login 会把用户重定向到登录页面，并显示一个错误提示。为了让这个重定向操作正确执行，
# 我们还需要把 login_manager.login_view 的值设为我们程序的登录视图端点（函数名）
login_manager.login_view = 'login'


# 如果你需要的话，可以通过设置 login_manager.login_message 来自定义错误提示消息。
# login_manager.login_message = 'Your custom message'


# 创建用户加载回调函数，接受用户 ID 作为参数
@login_manager.user_loader
def load_user(user_id):
    from watchlist.models import User
    # 用 ID 作为 User 模型的主键查询对应的用户
    user = User.query.get(int(user_id))
    return user


@app.context_processor
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    # 这个函数返回的变量（以字典键值对的形式）将会统一注入到每一个模板的上下文环境中，因此可以直接在模板中使用
    return dict(user=user)


from watchlist import views, commands, errors
