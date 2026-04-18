declare namespace API {
  type addUserApiUserAddPostParams = {
    SESSION?: string | null
  }

  type BaseResponseBool_ = {
    /** Code 状态码 */
    code?: number
    /** Data 响应数据 */
    data?: boolean | null
    /** Message 响应消息 */
    message?: string
  }

  type BaseResponseDict_ = {
    /** Code 状态码 */
    code?: number
    /** Data 响应数据 */
    data?: Record<string, any> | null
    /** Message 响应消息 */
    message?: string
  }

  type BaseResponseInt_ = {
    /** Code 状态码 */
    code?: number
    /** Data 响应数据 */
    data?: number | null
    /** Message 响应消息 */
    message?: string
  }

  type BaseResponseLoginUserVO_ = {
    /** Code 状态码 */
    code?: number
    /** 响应数据 */
    data?: LoginUserVO | null
    /** Message 响应消息 */
    message?: string
  }

  type BaseResponseStr_ = {
    /** Code 状态码 */
    code?: number
    /** Data 响应数据 */
    data?: string | null
    /** Message 响应消息 */
    message?: string
  }

  type BaseResponseUserVO_ = {
    /** Code 状态码 */
    code?: number
    /** 响应数据 */
    data?: UserVO | null
    /** Message 响应消息 */
    message?: string
  }

  type DeleteRequest = {
    /** Id 删除项的 ID */
    id: number
  }

  type deleteUserApiUserDeletePostParams = {
    SESSION?: string | null
  }

  type getLoginUserApiUserGetLoginGetParams = {
    SESSION?: string | null
  }

  type getUserByIdApiUserGetGetParams = {
    id: number
  }

  type HTTPValidationError = {
    /** Detail */
    detail?: ValidationError[]
  }

  type listUsersByPageApiUserListPagePostParams = {
    SESSION?: string | null
  }

  type LoginUserVO = {
    /** Id */
    id: number
    /** Useraccount */
    userAccount: string
    /** Username */
    userName?: string | null
    /** Useravatar */
    userAvatar?: string | null
    /** Userprofile */
    userProfile?: string | null
    /** Userrole */
    userRole: string
    /** Createtime */
    createTime: string
    /** Updatetime */
    updateTime: string
  }

  type logoutApiUserLogoutPostParams = {
    SESSION?: string | null
  }

  type updateUserApiUserUpdatePostParams = {
    SESSION?: string | null
  }

  type UserAddRequest = {
    /** Useraccount 账号 */
    userAccount: string
    /** Userpassword 密码 */
    userPassword: string
    /** Username 用户昵称 */
    userName?: string | null
    /** Useravatar 用户头像 */
    userAvatar?: string | null
    /** Userprofile 用户简介 */
    userProfile?: string | null
    /** Userrole 用户角色 */
    userRole?: string
  }

  type UserLoginRequest = {
    /** Useraccount 账号 */
    userAccount: string
    /** Userpassword 密码 */
    userPassword: string
  }

  type UserQueryRequest = {
    /** Current 当前页码 */
    current?: number
    /** Pagesize 每页大小 */
    pageSize?: number
    /** Sortfield 排序字段 */
    sortField?: string | null
    /** Sortorder 排序顺序 */
    sortOrder?: string | null
    /** Id 用户 ID */
    id?: number | null
    /** Useraccount 账号 */
    userAccount?: string | null
    /** Username 用户昵称 */
    userName?: string | null
    /** Userprofile 用户简介 */
    userProfile?: string | null
    /** Userrole 用户角色 */
    userRole?: string | null
  }

  type UserRegisterRequest = {
    /** Useraccount 账号 */
    userAccount: string
    /** Userpassword 密码 */
    userPassword: string
    /** Checkpassword 确认密码 */
    checkPassword: string
  }

  type UserUpdateRequest = {
    /** Id 用户 ID */
    id: number
    /** Username 用户昵称 */
    userName?: string | null
    /** Useravatar 用户头像 */
    userAvatar?: string | null
    /** Userprofile 用户简介 */
    userProfile?: string | null
    /** Userrole 用户角色 */
    userRole?: string | null
  }

  type UserVO = {
    /** Id */
    id: number
    /** Useraccount */
    userAccount: string
    /** Username */
    userName?: string | null
    /** Useravatar */
    userAvatar?: string | null
    /** Userprofile */
    userProfile?: string | null
    /** Userrole */
    userRole: string
    /** Createtime */
    createTime: string
  }

  type ValidationError = {
    /** Location */
    loc: (string | number)[]
    /** Message */
    msg: string
    /** Error Type */
    type: string
  }
}
