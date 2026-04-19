declare namespace API {
  type addUserApiUserAddPostParams = {
    SESSION?: string | null
  }

  type AgentExecutionStatsVO = {
    /** Taskid */
    taskId: string
    /** Totaldurationms */
    totalDurationMs: number
    /** Agentcount */
    agentCount: number
    /** Agentdurations */
    agentDurations?: Record<string, any>
    /** Overallstatus */
    overallStatus: string
    /** Logs */
    logs?: AgentLogVO[]
  }

  type AgentLogVO = {
    /** Id */
    id: number
    /** Taskid */
    taskId: string
    /** Agentname */
    agentName: string
    /** Starttime */
    startTime: string
    /** Endtime */
    endTime?: string | null
    /** Durationms */
    durationMs?: number | null
    /** Status */
    status: string
    /** Errormessage */
    errorMessage?: string | null
    /** Prompt */
    prompt?: string | null
    /** Inputdata */
    inputData?: string | null
    /** Outputdata */
    outputData?: string | null
    /** Createtime */
    createTime: string
    /** Updatetime */
    updateTime: string
  }

  type aiModifyOutlineApiBlogAiModifyOutlinePostParams = {
    SESSION?: string | null
  }

  type BaseResponseAgentExecutionStatsVO_ = {
    /** Code 状态码 */
    code?: number
    /** 响应数据 */
    data?: AgentExecutionStatsVO | null
    /** Message 响应消息 */
    message?: string
  }

  type BaseResponseBlogVO_ = {
    /** Code 状态码 */
    code?: number
    /** 响应数据 */
    data?: BlogVO | null
    /** Message 响应消息 */
    message?: string
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

  type BaseResponseList_ = {
    /** Code 状态码 */
    code?: number
    /** Data 响应数据 */
    data?: any[] | null
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

  type BaseResponseNoneType_ = {
    /** Code 状态码 */
    code?: number
    /** Data 响应数据 */
    data?: null
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

  type BlogAiModifyOutlineRequest = {
    /** Taskid */
    taskId: string
    /** Modifysuggestion */
    modifySuggestion: string
  }

  type BlogConfirmOutlineRequest = {
    /** Taskid */
    taskId: string
    /** Outline */
    outline: OutlineSection[]
  }

  type BlogConfirmTitleRequest = {
    /** Taskid */
    taskId: string
    /** Selectedmaintitle */
    selectedMainTitle: string
    /** Selectedsubtitle */
    selectedSubTitle: string
    /** Userdescription */
    userDescription?: string | null
  }

  type BlogCreateRequest = {
    /** Topic 选题 */
    topic: string
    /** Style 博客风格：tech/emotional/educational/humorous */
    style?: string | null
    /** Enabledimagemethods 允许的配图方式列表（为空表示支持所有方式） */
    enabledImageMethods?: string[] | null
  }

  type BlogQueryRequest = {
    /** Current 当前页码 */
    current?: number
    /** Pagesize 每页大小 */
    pageSize?: number
    /** Sortfield 排序字段 */
    sortField?: string | null
    /** Sortorder 排序顺序 */
    sortOrder?: string | null
    /** Id 博客 ID */
    id?: number | null
    /** Taskid 任务 ID */
    taskId?: string | null
    /** Userid 用户 ID */
    userId?: number | null
    /** Topic 选题 */
    topic?: string | null
    /** Status 状态 */
    status?: string | null
  }

  type BlogVO = {
    /** Id */
    id: number
    /** Taskid */
    taskId: string
    /** Userid */
    userId: number
    /** Topic */
    topic: string
    /** Userdescription */
    userDescription?: string | null
    /** Style */
    style?: string | null
    /** Maintitle */
    mainTitle?: string | null
    /** Subtitle */
    subTitle?: string | null
    /** Titleoptions */
    titleOptions?: TitleOption[] | null
    /** Outline */
    outline?: any[] | null
    /** Content */
    content?: string | null
    /** Fullcontent */
    fullContent?: string | null
    /** Coverimage */
    coverImage?: string | null
    /** Images */
    images?: any[] | null
    /** Status */
    status: string
    /** Phase */
    phase?: string | null
    /** Errormessage */
    errorMessage?: string | null
    /** Createtime */
    createTime: string
    /** Completedtime */
    completedTime?: string | null
    /** Updatetime */
    updateTime: string
  }

  type confirmOutlineApiBlogConfirmOutlinePostParams = {
    SESSION?: string | null
  }

  type confirmTitleApiBlogConfirmTitlePostParams = {
    SESSION?: string | null
  }

  type createBlogApiBlogCreatePostParams = {
    SESSION?: string | null
  }

  type deleteBlogApiBlogDeletePostParams = {
    SESSION?: string | null
  }

  type DeleteRequest = {
    /** Id 删除项的 ID */
    id: number
  }

  type deleteUserApiUserDeletePostParams = {
    SESSION?: string | null
  }

  type getBlogApiBlogTaskIdGetParams = {
    task_id: string
    SESSION?: string | null
  }

  type getExecutionLogsApiBlogExecutionLogsTaskIdGetParams = {
    task_id: string
  }

  type getLoginUserApiUserGetLoginGetParams = {
    SESSION?: string | null
  }

  type getProgressApiBlogProgressTaskIdGetParams = {
    task_id: string
    SESSION?: string | null
  }

  type getUserByIdApiUserGetGetParams = {
    id: number
  }

  type HTTPValidationError = {
    /** Detail */
    detail?: ValidationError[]
  }

  type listBlogApiBlogListPostParams = {
    SESSION?: string | null
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

  type OutlineSection = {
    /** Section */
    section: number
    /** Title */
    title: string
    /** Points */
    points: string[]
  }

  type TitleOption = {
    /** Maintitle */
    mainTitle: string
    /** Subtitle */
    subTitle: string
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
