import { errorResponse } from "../utils/http.js";

function isMissing(value) {
  return value === undefined || value === null || value === "";
}

function checkType(value, expectedType) {
  if (expectedType === "array") {
    return Array.isArray(value);
  }
  if (expectedType === "number") {
    return typeof value === "number" && Number.isFinite(value);
  }
  if (expectedType === "date") {
    return typeof value === "number" && Number.isFinite(value);
  }
  if (expectedType === "object") {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }
  return typeof value === expectedType;
}

function validateField(field, value, rule) {
  const errors = [];
  if (rule.required && isMissing(value)) {
    errors.push(`${field} is required`);
    return errors;
  }

  if (isMissing(value)) {
    return errors;
  }

  if (rule.type && !checkType(value, rule.type)) {
    errors.push(`${field} must be of type ${rule.type}`);
    return errors;
  }

  if (typeof value === "string") {
    if (typeof rule.min === "number" && value.length < rule.min) {
      errors.push(`${field} must be at least ${rule.min} characters`);
    }
    if (typeof rule.max === "number" && value.length > rule.max) {
      errors.push(`${field} must be at most ${rule.max} characters`);
    }
  }

  if (typeof value === "number") {
    if (typeof rule.min === "number" && value < rule.min) {
      errors.push(`${field} must be >= ${rule.min}`);
    }
    if (typeof rule.max === "number" && value > rule.max) {
      errors.push(`${field} must be <= ${rule.max}`);
    }
  }

  if (Array.isArray(value)) {
    if (typeof rule.min === "number" && value.length < rule.min) {
      errors.push(`${field} must contain at least ${rule.min} items`);
    }
    if (typeof rule.max === "number" && value.length > rule.max) {
      errors.push(`${field} must contain at most ${rule.max} items`);
    }
  }

  if (rule.enum && !rule.enum.includes(value)) {
    errors.push(`${field} must be one of: ${rule.enum.join(", ")}`);
  }

  if (rule.pattern) {
    const regex = rule.pattern instanceof RegExp ? rule.pattern : new RegExp(rule.pattern);
    if (typeof value !== "string" || !regex.test(value)) {
      errors.push(`${field} has invalid format`);
    }
  }

  return errors;
}

export function validate(schema, { source = "body", allowUnknown = true } = {}) {
  return async (req, next) => {
    const data = req[source];
    const target = data && typeof data === "object" ? data : {};
    const errors = [];

    if (!allowUnknown) {
      Object.keys(target).forEach((key) => {
        if (!schema[key]) {
          errors.push({
            field: key,
            message: `${key} is not allowed`,
          });
        }
      });
    }

    Object.entries(schema).forEach(([field, rule]) => {
      const fieldErrors = validateField(field, target[field], rule);
      fieldErrors.forEach((message) => errors.push({ field, message }));
    });

    if (errors.length > 0) {
      return errorResponse(400, "Validation failed", { fields: errors });
    }

    return next();
  };
}
