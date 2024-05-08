QUERY = """
    fields @timestamp, @message, @logStream, @log
    | sort @timestamp desc
    """
    
LOG_GROUP = """/codebuild/awslearning/aws_watermark"""
