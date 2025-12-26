"""Validación en runtime de implementaciones de interfaces.

Este módulo proporciona herramientas para verificar en runtime que las clases
implementan correctamente las interfaces abstractas, detectando errores
antes de que causen problemas en producción.

Uso:
    from shared.interface.validation import validate_implementation, ValidatedABC
    
    # Opción 1: Decorador
    @validate_implementation(IEventService)
    class EventService:
        ...
    
    # Opción 2: Metaclase (validación automática)
    class EventService(IEventService, metaclass=ValidatedABC):
        ...
"""
import inspect
from abc import ABC, ABCMeta
from typing import Any, Type, get_type_hints
from functools import wraps


class InterfaceValidationError(Exception):
    """Error lanzado cuando una clase no implementa correctamente una interfaz."""
    pass


def get_abstract_methods(cls: Type) -> set[str]:
    """Obtiene los métodos abstractos de una clase.
    
    Args:
        cls: Clase a inspeccionar
        
    Returns:
        set[str]: Conjunto de nombres de métodos abstractos
    """
    abstract_methods = set()
    
    for name in dir(cls):
        if name.startswith('_') and not name.startswith('__'):
            continue
            
        method = getattr(cls, name, None)
        if method is not None and getattr(method, '__isabstractmethod__', False):
            abstract_methods.add(name)
    
    return abstract_methods


def get_method_signature(method: Any) -> tuple[list[str], Any]:
    """Obtiene la firma de un método (parámetros y tipo de retorno).
    
    Args:
        method: Método a inspeccionar
        
    Returns:
        tuple: (lista de parámetros, tipo de retorno)
    """
    try:
        sig = inspect.signature(method)
        params = [
            name for name, param in sig.parameters.items() 
            if name != 'self'
        ]
        return_annotation = sig.return_annotation
        return params, return_annotation
    except (ValueError, TypeError):
        return [], inspect.Parameter.empty


def validate_method_signature(
    interface_method: Any,
    impl_method: Any,
    method_name: str,
    interface_name: str,
    impl_name: str
) -> list[str]:
    """Valida que la firma del método implementado sea compatible.
    
    Args:
        interface_method: Método de la interfaz
        impl_method: Método de la implementación
        method_name: Nombre del método
        interface_name: Nombre de la interfaz
        impl_name: Nombre de la implementación
        
    Returns:
        list[str]: Lista de errores encontrados
    """
    errors = []
    
    interface_params, interface_return = get_method_signature(interface_method)
    impl_params, impl_return = get_method_signature(impl_method)
    
    # Verificar que los parámetros obligatorios estén presentes
    # (permitimos parámetros adicionales con valores por defecto)
    for param in interface_params:
        if param not in impl_params:
            errors.append(
                f"  - Método '{method_name}': falta parámetro '{param}' "
                f"(definido en {interface_name})"
            )
    
    return errors


def validate_implementation(interface: Type) -> callable:
    """Decorador que valida que una clase implemente correctamente una interfaz.
    
    Verifica en el momento de definición de la clase:
    - Que todos los métodos abstractos estén implementados
    - Que las firmas de los métodos sean compatibles
    
    Args:
        interface: Interfaz que debe implementar la clase
        
    Returns:
        callable: Decorador que valida la clase
        
    Raises:
        InterfaceValidationError: Si la validación falla
        
    Ejemplo:
        @validate_implementation(IEventService)
        class EventService:
            async def create_event(self, event_data):
                ...
    """
    def decorator(cls: Type) -> Type:
        errors = []
        
        # Obtener métodos abstractos de la interfaz
        abstract_methods = get_abstract_methods(interface)
        
        for method_name in abstract_methods:
            interface_method = getattr(interface, method_name)
            impl_method = getattr(cls, method_name, None)
            
            # Verificar que el método existe
            if impl_method is None:
                errors.append(
                    f"  - Falta método '{method_name}' "
                    f"(requerido por {interface.__name__})"
                )
                continue
            
            # Verificar que no sigue siendo abstracto
            if getattr(impl_method, '__isabstractmethod__', False):
                errors.append(
                    f"  - Método '{method_name}' sigue siendo abstracto"
                )
                continue
            
            # Verificar firma del método
            signature_errors = validate_method_signature(
                interface_method,
                impl_method,
                method_name,
                interface.__name__,
                cls.__name__
            )
            errors.extend(signature_errors)
        
        if errors:
            error_msg = (
                f"\n{'='*60}\n"
                f"❌ ERROR DE VALIDACIÓN DE INTERFAZ\n"
                f"{'='*60}\n"
                f"Clase: {cls.__name__}\n"
                f"Interfaz: {interface.__name__}\n"
                f"\nProblemas encontrados:\n"
                + "\n".join(errors) +
                f"\n{'='*60}"
            )
            raise InterfaceValidationError(error_msg)
        
        # Añadir marca de que la clase fue validada
        cls._validated_interface = interface
        
        return cls
    
    return decorator


class ValidatedABCMeta(ABCMeta):
    """Metaclase que valida automáticamente implementaciones de interfaces.
    
    Combina la funcionalidad de ABCMeta con validación automática
    de que los métodos abstractos estén correctamente implementados.
    
    Uso:
        class IMyService(ABC, metaclass=ValidatedABCMeta):
            @abstractmethod
            async def my_method(self) -> str:
                pass
        
        class MyService(IMyService):  # Se valida automáticamente
            async def my_method(self) -> str:
                return "hello"
    """
    
    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        
        # No validar clases abstractas (solo las implementaciones concretas)
        if ABC in bases or any(getattr(base, '__abstractmethods__', None) for base in bases):
            # Es una clase abstracta, no validar aún
            abstract_methods = getattr(cls, '__abstractmethods__', set())
            if abstract_methods:
                return cls
        
        # Validar que todos los métodos abstractos estén implementados
        abstract_methods = getattr(cls, '__abstractmethods__', set())
        if abstract_methods:
            # Todavía tiene métodos abstractos sin implementar
            methods_list = ", ".join(sorted(abstract_methods))
            raise InterfaceValidationError(
                f"\n{'='*60}\n"
                f"❌ ERROR DE VALIDACIÓN DE INTERFAZ\n"
                f"{'='*60}\n"
                f"Clase: {name}\n"
                f"\nMétodos abstractos sin implementar:\n"
                f"  {methods_list}\n"
                f"{'='*60}"
            )
        
        return cls


def runtime_check(interface: Type):
    """Verifica en runtime que un objeto implemente una interfaz.
    
    Útil para validar objetos recibidos como parámetros.
    
    Args:
        interface: Interfaz esperada
        
    Returns:
        callable: Decorador para funciones/métodos
        
    Ejemplo:
        @runtime_check(IEventService)
        def process_events(service):
            # service está garantizado que implementa IEventService
            ...
    """
    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Buscar el primer argumento que no sea self
            check_args = args[1:] if args and hasattr(args[0], '__class__') else args
            
            for arg in check_args:
                if hasattr(arg, '__class__'):
                    # Verificar que implementa la interfaz
                    if not isinstance(arg, interface):
                        raise InterfaceValidationError(
                            f"Se esperaba un objeto que implemente {interface.__name__}, "
                            f"pero se recibió {type(arg).__name__}"
                        )
            
            return func(*args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            check_args = args[1:] if args and hasattr(args[0], '__class__') else args
            
            for arg in check_args:
                if hasattr(arg, '__class__'):
                    if not isinstance(arg, interface):
                        raise InterfaceValidationError(
                            f"Se esperaba un objeto que implemente {interface.__name__}, "
                            f"pero se recibió {type(arg).__name__}"
                        )
            
            return await func(*args, **kwargs)
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator

