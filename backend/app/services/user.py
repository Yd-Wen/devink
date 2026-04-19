"""用户服务"""
"""
管理员专用的接口需要校验权限，但如果在每个接口里都重复写一遍权限判断，代码会非常兄余。
FastAPI的依赖注入(Dependency Injection)系统提供了优雅的解法:
- 将通用的权限逻辑封装为可复用的依赖函数
- 在接口定义时通过 depends()声明需要哪个依赖
- FastAPI在接口被调用时自动执行对应的依赖函数，权限不足时直接终止请求，连接口处理函数都不会执行

定义依赖链:
- 从 Cookie 读取 Session ID
- 用 Session ID 查 Redis 获取用户信息
- 要求用户登录
- 要求用户是管理员

使用时非常简洁:
- 公开接口不加任何依赖，
- 需要登录才能访问的接口加 Depends(require_login)
- 仅管理员可访问的接口加 Depends(require_admin)
FastAPI 会在请求进来时自动完成校验
"""
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_, or_
from databases import Database

from app.models.user import User
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserAddRequest,
    UserUpdateRequest,
    UserQueryRequest,
    UserVO,
    LoginUserVO
)
from app.constants.user import UserConstant
from app.exceptions import ErrorCode, throw_if, throw_if_not, BusinessException
from app.utils.password import encrypt_password


class UserService:
    """用户服务"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def register(self, request: UserRegisterRequest) -> int:
        """用户注册"""
        # 校验参数
        throw_if(
            len(request.user_account) < 4,
            ErrorCode.PARAMS_ERROR,
            "账号长度不能小于 4 位"
        )
        throw_if(
            len(request.user_password) < 8,
            ErrorCode.PARAMS_ERROR,
            "密码长度不能小于 8 位"
        )
        throw_if(
            request.user_password != request.check_password,
            ErrorCode.PARAMS_ERROR,
            "两次输入的密码不一致"
        )
        
        # 检查账号是否已存在
        query = select(func.count(User.id)).where(
            and_(User.user_account == request.user_account, User.is_delete == 0)
        )
        count = await self.db.fetch_val(query)
        throw_if(count > 0, ErrorCode.USER_ALREADY_EXIST, "账号已存在")
        
        # 加密密码
        encrypted_password = encrypt_password(request.user_password)
        
        # 插入用户
        query = """
            INSERT INTO user (userAccount, userPassword, userName, userRole, quota)
            VALUES (:userAccount, :userPassword, :userName, :userRole, :quota)
        """
        user_id = await self.db.execute(
            query=query,
            values={
                "userAccount": request.user_account,
                "userPassword": encrypted_password,
                "userName": f"用户{request.user_account}",
                "userRole": UserConstant.DEFAULT_ROLE,
                "quota": UserConstant.DEFAULT_QUOTA,
            }
        )
        
        return user_id
    
    async def login(self, request: UserLoginRequest) -> LoginUserVO:
        """用户登录"""
        # 校验参数
        throw_if(
            len(request.user_account) < 4,
            ErrorCode.PARAMS_ERROR,
            "账号长度不能小于 4 位"
        )
        throw_if(
            len(request.user_password) < 8,
            ErrorCode.PARAMS_ERROR,
            "密码长度不能小于 8 位"
        )
        
        # 查询用户
        query = select(User).where(
            and_(User.user_account == request.user_account, User.is_delete == 0)
        )
        user = await self.db.fetch_one(query)
        throw_if_not(user, ErrorCode.USER_NOT_EXIST, "用户不存在")
        
        # 验证密码
        encrypted_password = encrypt_password(request.user_password)
        throw_if(
            user["userPassword"] != encrypted_password,
            ErrorCode.PASSWORD_ERROR,
            "密码错误"
        )

        user_dict = dict(user)
        
        # 返回登录用户信息
        return LoginUserVO(
            id=user_dict["id"],
            userAccount=user_dict["userAccount"],
            userName=user_dict["userName"],
            userAvatar=user_dict["userAvatar"],
            userDescription=user_dict["userDescription"],
            userRole=user_dict["userRole"],
            quota=user_dict.get("quota"),
            createTime=user_dict["createTime"].isoformat(),
            updateTime=user_dict["updateTime"].isoformat()
        )
    
    async def get_by_id(self, user_id: int) -> Optional[UserVO]:
        """根据 ID 获取用户"""
        query = select(User).where(and_(User.id == user_id, User.is_delete == 0))
        user = await self.db.fetch_one(query)
        
        if not user:
            return None

        user_dict = dict(user)
        
        return UserVO(
            id=user_dict["id"],
            userAccount=user_dict["userAccount"],
            userName=user_dict["userName"],
            userAvatar=user_dict["userAvatar"],
            userDescription=user_dict["userDescription"],
            userRole=user_dict["userRole"],
            quota=user_dict.get("quota"),
            createTime=user_dict["createTime"].isoformat()
        )
    
    async def list_by_page(self, request: UserQueryRequest) -> Tuple[List[UserVO], int]:
        """分页查询用户列表"""
        # 构建查询条件
        conditions = [User.is_delete == 0]
        
        if request.id:
            conditions.append(User.id == request.id)
        if request.user_account:
            conditions.append(User.user_account.like(f"%{request.user_account}%"))
        if request.user_name:
            conditions.append(User.user_name.like(f"%{request.user_name}%"))
        if request.user_description:
            conditions.append(User.user_description.like(f"%{request.user_description}%"))
        if request.user_role:
            conditions.append(User.user_role == request.user_role)
        
        # 查询总数
        count_query = select(func.count(User.id)).where(and_(*conditions))
        total = await self.db.fetch_val(count_query)
        
        # 分页查询
        query = select(User).where(and_(*conditions))
        
        # 排序
        if request.sort_field:
            order_column = getattr(User, request.sort_field, None)
            if order_column is not None:
                if request.sort_order == "ascend":
                    query = query.order_by(order_column.asc())
                else:
                    query = query.order_by(order_column.desc())
        else:
            query = query.order_by(User.create_time.desc())
        
        # 分页
        offset = (request.current - 1) * request.page_size
        query = query.limit(request.page_size).offset(offset)
        
        users = await self.db.fetch_all(query)
        
        user_list = []
        for user in users:
            user_dict = dict(user)
            user_list.append(
                UserVO(
                    id=user_dict["id"],
                    userAccount=user_dict["userAccount"],
                    userName=user_dict["userName"],
                    userAvatar=user_dict["userAvatar"],
                    userDescription=user_dict["userDescription"],
                    userRole=user_dict["userRole"],
                    quota=user_dict.get("quota"),
                    createTime=user_dict["createTime"].isoformat()
                )
            )
        
        return user_list, total
    
    async def add_user(self, request: UserAddRequest) -> int:
        """添加用户（管理员）"""
        # 校验账号是否已存在
        query = select(func.count(User.id)).where(
            and_(User.user_account == request.user_account, User.is_delete == 0)
        )
        count = await self.db.fetch_val(query)
        throw_if(count > 0, ErrorCode.USER_ALREADY_EXIST, "账号已存在")
        
        # 加密密码
        encrypted_password = encrypt_password(request.user_password)
        
        # 插入用户
        query = """
            INSERT INTO user (userAccount, userPassword, userName, userAvatar, userDescription, userRole, quota)
            VALUES (:userAccount, :userPassword, :userName, :userAvatar, :userDescription, :userRole, :quota)
        """
        user_id = await self.db.execute(
            query=query,
            values={
                "userAccount": request.user_account,
                "userPassword": encrypted_password,
                "userName": request.user_name or f"用户{request.user_account}",
                "userAvatar": request.user_avatar,
                "userDescription": request.user_description,
                "userRole": request.user_role,
                "quota": UserConstant.DEFAULT_QUOTA,
            }
        )
        
        return user_id
    
    async def update_user(self, request: UserUpdateRequest) -> bool:
        """更新用户（管理员）"""
        # 检查用户是否存在
        query = select(func.count(User.id)).where(and_(User.id == request.id, User.is_delete == 0))
        count = await self.db.fetch_val(query)
        throw_if(count == 0, ErrorCode.NOT_FOUND_ERROR, "用户不存在")
        
        # 构建更新字段
        update_fields = []
        values = {"id": request.id}
        
        if request.user_name is not None:
            update_fields.append("userName = :userName")
            values["userName"] = request.user_name
        
        if request.user_avatar is not None:
            update_fields.append("userAvatar = :userAvatar")
            values["userAvatar"] = request.user_avatar
        
        if request.user_description is not None:
            update_fields.append("userDescription = :userDescription")
            values["userDescription"] = request.user_description
        
        if request.user_role is not None:
            update_fields.append("userRole = :userRole")
            values["userRole"] = request.user_role
        
        throw_if(len(update_fields) == 0, ErrorCode.PARAMS_ERROR, "没有需要更新的字段")
        
        # 执行更新
        query = f"UPDATE user SET {', '.join(update_fields)} WHERE id = :id"
        await self.db.execute(query=query, values=values)
        
        return True
    
    async def delete_user(self, user_id: int) -> bool:
        """删除用户（逻辑删除）"""
        # 检查用户是否存在
        query = select(func.count(User.id)).where(and_(User.id == user_id, User.is_delete == 0))
        count = await self.db.fetch_val(query)
        throw_if(count == 0, ErrorCode.NOT_FOUND_ERROR, "用户不存在")
        
        # 逻辑删除
        query = "UPDATE user SET isDelete = 1 WHERE id = :id"
        await self.db.execute(query=query, values={"id": user_id})
        
        return True
