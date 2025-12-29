search_course = {
    "type": "function",
    "function": {
        "name": "search_course",
        "description":
            "根据给定的条件，在网上爬取符合要求的课程信息列表。返回值包括查找到多少个课程，分为几页展示，以及每个课程的具体信息。"
            "（每个课程的具体信息包括开课院系、课程号、课序号、课程名、学分、主讲教师、本科生课容量、本科生课余量、研究生课容量、"
            "研究生课余量、上课时间、选课文字说明、课程特色、年级、是否二级选课、实验信息、重修是否占容量、是否选课时限制、通识选修课组。）"
        ,
        "parameters": {
            "type": "object",
            "properties": {
                "course_id": {
                    "type": "string",
                    "description": "想要查询课程的课程号",
                    "default": ''
                },
                "course_name": {
                    "type": "string",
                    "description": "想要查询的课程名",
                    "default": ''
                },
                "teacher_name": {
                    "type": "string",
                    "description": "想要查找哪位老师的课",
                    "default": ''
                },
                "is_general": {
                    "type": "boolean",
                    "description": "是否一定要是通识任选课",
                    "default": ''
                },
                "max_page":{
                    "type": "integer",
                    "description": "若结果很多导致分页，当前要查看前多少几页",
                    "default": 3
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


search_situation = {
    "type": "function",
    "function": {
        "name": "search_situation",
        "description": "根据给定的条件，在网上爬取符合要求的课程的选课情况列表（主要是为了查询课余量和队列人数）。"
                       "返回值包括查找到多少个课程，分为几页展示，以及每个课程的具体选课情况"
                       "（主要可查看当前课程选课人数以及Waiting List中的人数）。",
        "parameters": {
            "type": "object",
            "properties": {
                "course_id": {
                    "type": "string",
                    "description": "想要查询课程的课程号",
                    "default": ''
                },
                "course_name": {
                    "type": "string",
                    "description": "想要查询的课程名",
                    "default": ''
                },
                "course_rank": {
                    "type": "string",
                    "description": "想要查找课程的课序号",
                    "default": ''
                },
                "max_page":{
                    "type": "integer",
                    "description": "若结果很多导致分页，当前要查看前多少页",
                    "default": 3
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
}


search_teacher = {
    "type": "function",
    "function": {
        "name": "search_teacher",
        "description": "查找某一位老师所开过的课程收获过的学生评价。返回值包括该老师有几门课有学生评价，"
                       "学生给他每门课打的平均分，以及具体评价。",
        "parameters": {
            "type": "object",
            "properties": {
                "teacher":{
                    "type": "string",
                    "description": "想要查找的老师",
                }
            },
            "required": ["teacher"],
            "additionalProperties": False
        }
    }
}


search_user_table = {
    "type": "function",
    "function": {
        "name": "search_user_table",
        "description": "查看用户当前已选择的课程。注意，由于只有当系统提示你可以查看时，你才可以查看。",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }

    }
}


tools = [search_course, search_situation, search_teacher, search_user_table]
