import re
from typing import List, Dict, Any, Optional
from app.domain.schemas import VariableDefinition


class TemplateService:
    VARIABLE_PATTERN = re.compile(r'\{\{(\w+)\}\}')

    def parse_variables(self, content: str) -> List[str]:
        matches = self.VARIABLE_PATTERN.findall(content)
        return list(set(matches))

    def validate_variables(self, content: str, variables: List[VariableDefinition]) -> Dict[str, Any]:
        defined_names = {v.name for v in variables}
        used_names = set(self.parse_variables(content))
        
        missing = used_names - defined_names
        unused = defined_names - used_names
        
        return {
            "valid": len(missing) == 0,
            "missing": list(missing),
            "unused": list(unused),
            "defined": list(defined_names),
            "used": list(used_names)
        }

    def instantiate(self, content: str, variables: List[VariableDefinition], 
                    values: Dict[str, Any]) -> str:
        result = content
        
        for var in variables:
            var_name = var.name
            var_value = values.get(var_name, var.default)
            
            if var.required and var_value is None:
                raise ValueError(f"Required variable '{var_name}' is missing")
            
            if var_value is not None:
                result = result.replace(f'{{{{{var_name}}}}}', str(var_value))
        
        remaining = self.parse_variables(result)
        if remaining:
            raise ValueError(f"Unresolved variables: {remaining}")
        
        return result

    def get_variable_defaults(self, variables: List[VariableDefinition]) -> Dict[str, Any]:
        return {v.name: v.default for v in variables if v.default is not None}