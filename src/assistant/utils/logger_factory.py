"""Logger factory for component-specific logging."""

from typing import Dict, Any, Optional, Union, Type
from pathlib import Path
import threading
import inspect
from functools import wraps

from .logging import AssistantLogger, logger_manager, get_logger


class LoggerFactory:
    """Factory for creating component-specific loggers with automatic configuration."""
    
    def __init__(self, base_config: Optional[Dict[str, Any]] = None):
        """Initialize logger factory.
        
        Args:
            base_config: Base configuration for all loggers
        """
        self.base_config = base_config or {}
        self._component_configs: Dict[str, Dict[str, Any]] = {}
        self._cache: Dict[str, AssistantLogger] = {}
        self._lock = threading.Lock()
    
    def register_component(self, component_name: str, config: Dict[str, Any]) -> None:
        """Register configuration for a specific component.
        
        Args:
            component_name: Name of the component
            config: Configuration specific to this component
        """
        self._component_configs[component_name] = config
    
    def get_component_logger(
        self,
        component_name: str,
        module_name: Optional[str] = None,
        instance_id: Optional[str] = None,
        **kwargs
    ) -> AssistantLogger:
        """Get logger for a specific component.
        
        Args:
            component_name: Name of the component
            module_name: Optional module name for more specific logging
            instance_id: Optional instance identifier
            **kwargs: Additional configuration overrides
            
        Returns:
            Component-specific logger
        """
        # Create cache key
        cache_key = f"{component_name}:{module_name}:{instance_id}"
        
        with self._lock:
            if cache_key in self._cache:
                logger = self._cache[cache_key]
            else:
                # Build configuration
                config = self._build_component_config(
                    component_name, module_name, instance_id, **kwargs
                )
                
                # Create logger name
                logger_name = f"assistant.{component_name}"
                if module_name:
                    logger_name += f".{module_name}"
                if instance_id:
                    logger_name += f".{instance_id}"
                
                # Determine log file path
                if "log_file" not in config and "log_dir" in config:
                    log_dir = Path(config["log_dir"])
                    log_dir.mkdir(parents=True, exist_ok=True)
                    config["log_file"] = str(log_dir / f"{component_name}.log")
                
                # Create logger
                logger = AssistantLogger(
                    name=logger_name,
                    **config
                )
                
                # Set component context
                logger.set_context(
                    component=component_name,
                    module=module_name,
                    instance_id=instance_id
                )
                
                self._cache[cache_key] = logger
        
        return logger
    
    def _build_component_config(
        self,
        component_name: str,
        module_name: Optional[str] = None,
        instance_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build configuration for a specific component."""
        # Start with base config
        config = self.base_config.copy()
        
        # Override with component-specific config
        if component_name in self._component_configs:
            config.update(self._component_configs[component_name])
        
        # Override with instance-specific config
        config.update(kwargs)
        
        return config
    
    def create_logger_for_class(self, cls: Type, instance_id: Optional[str] = None) -> AssistantLogger:
        """Create logger for a specific class.
        
        Args:
            cls: The class to create logger for
            instance_id: Optional instance identifier
            
        Returns:
            Logger for the class
        """
        component_name = cls.__module__.split('.')[-1]
        class_name = cls.__name__
        
        return self.get_component_logger(
            component_name=component_name,
            module_name=class_name,
            instance_id=instance_id
        )
    
    def create_logger_for_function(self, func: callable) -> AssistantLogger:
        """Create logger for a specific function.
        
        Args:
            func: The function to create logger for
            
        Returns:
            Logger for the function
        """
        module_name = func.__module__
        function_name = func.__name__
        component_name = module_name.split('.')[-1]
        
        return self.get_component_logger(
            component_name=component_name,
            module_name=function_name
        )
    
    def clear_cache(self) -> None:
        """Clear logger cache."""
        with self._lock:
            self._cache.clear()
    
    def get_cached_loggers(self) -> Dict[str, AssistantLogger]:
        """Get all cached loggers."""
        with self._lock:
            return self._cache.copy()


# Global logger factory instance
logger_factory = LoggerFactory()


def component_logger(
    component_name: Optional[str] = None,
    module_name: Optional[str] = None,
    instance_id: Optional[str] = None,
    **config
):
    """Decorator to automatically add logger to class or function.
    
    Args:
        component_name: Component name for the logger
        module_name: Module name for the logger
        instance_id: Instance identifier
        **config: Additional logger configuration
    """
    def decorator(target):
        if inspect.isclass(target):
            return _add_logger_to_class(target, component_name, module_name, instance_id, config)
        elif inspect.isfunction(target):
            return _add_logger_to_function(target, component_name, module_name, config)
        else:
            raise ValueError("Decorator can only be applied to classes or functions")
    
    return decorator


def _add_logger_to_class(
    cls: Type,
    component_name: Optional[str],
    module_name: Optional[str],
    instance_id: Optional[str],
    config: Dict[str, Any]
) -> Type:
    """Add logger to class."""
    # Store logger creation parameters
    cls._logger_config = {
        'component_name': component_name or cls.__module__.split('.')[-1],
        'module_name': module_name or cls.__name__,
        'instance_id': instance_id,
        'config': config
    }
    
    # Add logger property
    def get_logger(self):
        if not hasattr(self, '_instance_logger'):
            instance_id = getattr(self, 'id', None) or getattr(self, 'instance_id', None)
            self._instance_logger = logger_factory.get_component_logger(
                component_name=cls._logger_config['component_name'],
                module_name=cls._logger_config['module_name'],
                instance_id=instance_id,
                **cls._logger_config['config']
            )
        
        return self._instance_logger
    
    cls.logger = property(get_logger)
    
    return cls


def _add_logger_to_function(
    func: callable,
    component_name: Optional[str],
    module_name: Optional[str],
    config: Dict[str, Any]
) -> callable:
    """Add logger to function."""
    # Get component and module names from function if not provided
    func_component = component_name or func.__module__.split('.')[-1]
    func_module = module_name or func.__name__
    
    # Create logger for function
    logger = logger_factory.get_component_logger(
        component_name=func_component,
        module_name=func_module,
        **config
    )
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get logger instance for this call
        call_logger = logger_factory.get_component_logger(
            component_name=func_component,
            module_name=func_module,
            **config
        )
        
        # Log function call
        call_logger.log_function_call(
            func_name=func.__name__,
            args=args,
            kwargs=kwargs
        )
        
        # Execute function
        import time
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log successful result
            call_logger.log_function_result(
                func_name=func.__name__,
                result=result,
                execution_time=execution_time
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log error
            call_logger.exception(
                f"Function {func.__name__} failed",
                execution_time=execution_time,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            raise
    
    return wrapper


def log_method_calls(
    log_args: bool = True,
    log_result: bool = True,
    log_exceptions: bool = True,
    execution_time_threshold: Optional[float] = None
):
    """Decorator for logging method calls with configurable options.
    
    Args:
        log_args: Whether to log method arguments
        log_result: Whether to log method result
        log_exceptions: Whether to log exceptions
        execution_time_threshold: Log warning if execution exceeds threshold (seconds)
    """
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Get logger from class
            if hasattr(self, 'logger'):
                logger = self.logger
            else:
                # Fallback to logger factory
                logger = logger_factory.create_logger_for_class(self.__class__)
            
            # Prepare log data
            log_data = {
                'method': method.__name__,
                'class': self.__class__.__name__
            }
            
            if log_args:
                log_data['args_count'] = len(args)
                log_data['kwargs_keys'] = list(kwargs.keys())
            
            logger.debug("Method called", **log_data)
            
            # Execute method
            import time
            start_time = time.time()
            
            try:
                result = method(self, *args, **kwargs)
                execution_time = time.time() - start_time
                
                # Prepare result log data
                result_data = {
                    'method': method.__name__,
                    'class': self.__class__.__name__,
                    'execution_time_ms': round(execution_time * 1000, 2)
                }
                
                if execution_time_threshold and execution_time > execution_time_threshold:
                    log_data['execution_time_threshold'] = execution_time_threshold
                    logger.warning("Method execution exceeded threshold", **result_data)
                else:
                    logger.debug("Method completed", **result_data)
                
                if log_result:
                    result_data['result_type'] = type(result).__name__
                    logger.debug("Method result", **result_data)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                if log_exceptions:
                    exception_data = {
                        'method': method.__name__,
                        'class': self.__class__.__name__,
                        'execution_time_ms': round(execution_time * 1000, 2),
                        'error_type': type(e).__name__,
                        'error_message': str(e)
                    }
                    logger.exception("Method failed", **exception_data)
                
                raise
        
        return wrapper
    return decorator


# Convenience functions
def get_component_logger(component_name: str, **kwargs) -> AssistantLogger:
    """Get logger for a component using global factory."""
    return logger_factory.get_component_logger(component_name, **kwargs)


def register_component_logging(component_name: str, config: Dict[str, Any]) -> None:
    """Register component logging configuration."""
    logger_factory.register_component(component_name, config)