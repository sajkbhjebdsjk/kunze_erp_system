from flask import request, jsonify, g
from datetime import datetime, timedelta
import time
from collections import defaultdict

class RateLimiter:
    """请求限流器"""
    
    def __init__(self):
        # 存储每个IP的请求记录 {ip: [timestamp1, timestamp2, ...]}
        self.requests = defaultdict(list)
        # 默认限制：每分钟60次请求
        self.default_limit = 60
        self.default_window = 60  # 秒
        # 特殊端点的限制
        self.special_limits = {
            '/api/login': {'limit': 5, 'window': 60},  # 登录接口：每分钟5次
            '/api/riders': {'limit': 30, 'window': 60},  # 骑手查询：每分钟30次
        }
    
    def is_allowed(self, ip_address, endpoint=None):
        """检查是否允许请求"""
        current_time = time.time()
        
        # 获取该端点的限制
        if endpoint and endpoint in self.special_limits:
            limit = self.special_limits[endpoint]['limit']
            window = self.special_limits[endpoint]['window']
        else:
            limit = self.default_limit
            window = self.default_window
        
        # 清理过期的请求记录
        cutoff_time = current_time - window
        self.requests[ip_address] = [
            req_time for req_time in self.requests[ip_address] 
            if req_time > cutoff_time
        ]
        
        # 检查是否超过限制
        if len(self.requests[ip_address]) >= limit:
            return False
        
        # 记录本次请求
        self.requests[ip_address].append(current_time)
        return True
    
    def get_remaining_requests(self, ip_address, endpoint=None):
        """获取剩余请求数"""
        current_time = time.time()
        
        if endpoint and endpoint in self.special_limits:
            limit = self.special_limits[endpoint]['limit']
            window = self.special_limits[endpoint]['window']
        else:
            limit = self.default_limit
            window = self.default_window
        
        # 清理过期记录
        cutoff_time = current_time - window
        self.requests[ip_address] = [
            req_time for req_time in self.requests[ip_address]
            if req_time > cutoff_time
        ]
        
        return max(0, limit - len(self.requests[ip_address]))

# 全局限流器实例
rate_limiter = RateLimiter()

def rate_limit(f):
    """限流装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        ip_address = request.remote_addr
        endpoint = request.endpoint
        
        if not rate_limiter.is_allowed(ip_address, endpoint):
            remaining = rate_limiter.get_remaining_requests(ip_address, endpoint)
            response = jsonify({
                'success': False,
                'message': '请求过于频繁，请稍后再试',
                'retry_after': 60,
                'remaining': remaining
            })
            response.status_code = 429
            return response
        
        # 添加限流相关响应头
        response = f(*args, **kwargs)
        if hasattr(response, 'headers'):
            remaining = rate_limiter.get_remaining_requests(ip_address, endpoint)
            response.headers['X-RateLimit-Limit'] = str(
                rate_limiter.special_limits.get(endpoint, {}).get('limit', rate_limiter.default_limit)
            )
            response.headers['X-RateLimit-Remaining'] = str(remaining)
        
        return response
    
    return decorated

# 需要导入wraps
from functools import wraps
