import inspect
import pkgutil
import sys


class ClassUtil:
    @staticmethod
    def get_subtypes_of(base_class, package_name=None):
        """
        Finds all sub-types of a given base_class within specified packages or all loaded modules.

        Args:
            base_class: The base class to find sub-types for.
            package_name: Optional. The name of the package to scan. If None, scans all loaded modules.

        Returns:
            A set of sub-type classes.
        """
        sub_types = set()
        if (package_name is not None) and not (package_name.startswith("com.github.dm0896665.main.")):
            package_name = "com.github.dm0896665.main." + package_name

        if package_name:
            # Scan classes within a specific package
            for importer, modname, ispkg in pkgutil.iter_modules(sys.modules[package_name].__path__):
                try:
                    module = __import__(f"{package_name}.{modname}", fromlist=[modname])
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, base_class) and obj is not base_class:
                            sub_types.add(obj())
                except ImportError:
                    pass  # Handle cases where modules might not be importable
        else:
            # Scan classes in all currently loaded modules
            for module_name, module in sys.modules.items():
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, base_class) and obj is not base_class:
                        sub_types.add(obj())
        return sub_types