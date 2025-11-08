"""Middleware for cross-cutting concerns like performance monitoring."""

from .performance import init_performance_monitoring

__all__ = ["init_performance_monitoring"]
