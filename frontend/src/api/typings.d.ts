declare namespace API {
    type AgentExecutionStats = {
        taskId?: string
        totalDurationMs?: number
        agentCount?: number
        agentDurations?: Record<string, any>
        overallStatus?: string
        logs?: AgentLog[]
    }

    type AgentLog = {
        id?: number
        taskId?: string
        agentName?: string
        startTime?: string
        endTime?: string
        durationMs?: number
        status?: string
        errorMessage?: string
        prompt?: string
        inputData?: string
        outputData?: string
        createTime?: string
        updateTime?: string
        isDelete?: number
    }

    type BlogAiModifyOutlineRequest = {
        taskId?: string
        modifySuggestion?: string
    }

    type BlogConfirmOutlineRequest = {
        taskId?: string
        outline?: OutlineSection[]
    }

    type BlogConfirmTitleRequest = {
        taskId?: string
        selectedMainTitle?: string
        selectedSubTitle?: string
        userDescription?: string
    }

    type BlogCreateRequest = {
        topic?: string
        style?: string
        enabledImageMethods?: string[]
    }

    type BlogQueryRequest = {
        pageNum?: number
        pageSize?: number
        sortField?: string
        sortOrder?: string
        userId?: number
        status?: string
    }

    type BlogVO = {
        id?: number
        taskId?: string
        userId?: number
        topic?: string
        userDescription?: string
        mainTitle?: string
        subTitle?: string
        titleOptions?: TitleOption[]
        outline?: OutlineItem[]
        content?: string
        fullContent?: string
        coverImage?: string
        images?: ImageItem[]
        status?: string
        phase?: string
        errorMessage?: string
        createTime?: string
        completedTime?: string
    }

    type BaseResponseAgentExecutionStats = {
        code?: number
        data?: AgentExecutionStats
        message?: string
    }

    type BaseResponseBlogVO = {
        code?: number
        data?: BlogVO
        message?: string
    }

    type BaseResponseBoolean = {
        code?: number
        data?: boolean
        message?: string
    }

    type BaseResponseListOutlineSection = {
        code?: number
        data?: OutlineSection[]
        message?: string
    }

    type BaseResponseLoginUserVO = {
        code?: number
        data?: LoginUserVO
        message?: string
    }

    type BaseResponseLong = {
        code?: number
        data?: number
        message?: string
    }

    type BaseResponsePageBlogVO = {
        code?: number
        data?: PageBlogVO
        message?: string
    }

    type BaseResponsePageUserVO = {
        code?: number
        data?: PageUserVO
        message?: string
    }

    type BaseResponseStatisticsVO = {
        code?: number
        data?: StatisticsVO
        message?: string
    }

    type BaseResponseString = {
        code?: number
        data?: string
        message?: string
    }

    type BaseResponseUser = {
        code?: number
        data?: User
        message?: string
    }

    type BaseResponseUserVO = {
        code?: number
        data?: UserVO
        message?: string
    }

    type BaseResponseVoid = {
        code?: number
        data?: Record<string, any>
        message?: string
    }

    type DeleteRequest = {
        id?: number
    }

    type getBlogParams = {
        taskId: string
    }

    type getExecutionLogsParams = {
        taskId: string
    }

    type getProgressParams = {
        taskId: string
    }

    type getUserByIdParams = {
        id: number
    }

    type getUserVOByIdParams = {
        id: number
    }

    type ImageItem = {
        position?: number
        url?: string
        method?: string
        keywords?: string
        sectionTitle?: string
        description?: string
    }

    type LoginUserVO = {
        id?: number
        userAccount?: string
        userName?: string
        userAvatar?: string
        userProfile?: string
        userRole?: string
        quota?: number
        vipTime?: string
        createTime?: string
        updateTime?: string
    }

    type OutlineItem = {
        section?: number
        title?: string
        points?: string[]
    }

    type OutlineSection = {
        section?: number
        title?: string
        points?: string[]
    }

    type PageBlogVO = {
        records?: BlogVO[]
        pageNumber?: number
        pageSize?: number
        totalPage?: number
        totalRow?: number
        optimizeCountQuery?: boolean
    }

    type PageUserVO = {
        records?: UserVO[]
        pageNumber?: number
        pageSize?: number
        totalPage?: number
        totalRow?: number
        optimizeCountQuery?: boolean
    }

    type refundParams = {
        reason?: string
    }

    type SseEmitter = {
        timeout?: number
    }

    type StatisticsVO = {
        todayCount?: number
        weekCount?: number
        monthCount?: number
        totalCount?: number
        successRate?: number
        avgDurationMs?: number
        activeUserCount?: number
        totalUserCount?: number
        vipUserCount?: number
        quotaUsed?: number
    }

    type TitleOption = {
        mainTitle?: string
        subTitle?: string
    }

    type User = {
        id?: number
        userAccount?: string
        userPassword?: string
        userName?: string
        userAvatar?: string
        userProfile?: string
        userRole?: string
        quota?: number
        vipTime?: string
        editTime?: string
        createTime?: string
        updateTime?: string
        isDelete?: number
    }

    type UserAddRequest = {
        userName?: string
        userAccount?: string
        userAvatar?: string
        userProfile?: string
        userRole?: string
    }

    type UserLoginRequest = {
        userAccount?: string
        userPassword?: string
    }

    type UserQueryRequest = {
        pageNum?: number
        pageSize?: number
        sortField?: string
        sortOrder?: string
        id?: number
        userName?: string
        userAccount?: string
        userProfile?: string
        userRole?: string
    }

    type UserRegisterRequest = {
        userAccount?: string
        userPassword?: string
        checkPassword?: string
    }

    type UserUpdateRequest = {
        id?: number
        userName?: string
        userAvatar?: string
        userProfile?: string
        userRole?: string
    }

    type UserVO = {
        id?: number
        userAccount?: string
        userName?: string
        userAvatar?: string
        userProfile?: string
        userRole?: string
        createTime?: string
    }
}
