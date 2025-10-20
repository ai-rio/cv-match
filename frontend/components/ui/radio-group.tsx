/**
 * Enhanced Radio Group Component for CV-Match Phase 0.8
 *
 * Brazilian market optimized radio group with full design system integration
 * WCAG 2.1 AA compliant with excellent accessibility
 *
 * Features:
 * - Multiple radio options
 * - Brazilian market touch optimization
 * - Full keyboard navigation support
 * - Error handling
 * - Custom styling
 */

'use client';

import * as React from 'react';

import { cn } from '@/lib/utils';

export interface RadioGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: string;
  onValueChange?: (value: string) => void;
  defaultValue?: string;
  disabled?: boolean;
  name?: string;
  required?: boolean;
  orientation?: 'horizontal' | 'vertical';
}

export interface RadioGroupItemProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  value: string;
  label?: string;
  description?: string;
  disabled?: boolean;
  required?: boolean;
  id?: string;
}

const RadioGroupContext = React.createContext<{
  value?: string;
  onValueChange?: (value: string) => void;
  name?: string;
  disabled?: boolean;
  required?: boolean;
}>({});

const RadioGroup = React.forwardRef<HTMLDivElement, RadioGroupProps>(
  (
    {
      className,
      value,
      onValueChange,
      defaultValue,
      disabled = false,
      name,
      required = false,
      orientation = 'vertical',
      children,
      ...props
    },
    ref
  ) => {
    const [internalValue, setInternalValue] = React.useState(defaultValue || '');

    // Update internal value when controlled prop changes
    React.useEffect(() => {
      if (value !== undefined) {
        setInternalValue(value);
      }
    }, [value]);

    const handleChange = (newValue: string) => {
      setInternalValue(newValue);
      onValueChange?.(newValue);
    };

    return (
      <RadioGroupContext.Provider
        value={{
          value: value !== undefined ? value : internalValue,
          onValueChange: handleChange,
          name,
          disabled,
          required,
        }}
      >
        <div
          ref={ref}
          className={cn(
            'grid gap-2',
            orientation === 'horizontal' ? 'grid-flow-col auto-cols-max' : 'grid-cols-1',
            className
          )}
          role="radiogroup"
          aria-required={required}
          {...props}
        >
          {children}
        </div>
      </RadioGroupContext.Provider>
    );
  }
);

RadioGroup.displayName = 'RadioGroup';

const RadioGroupItem = React.forwardRef<HTMLInputElement, RadioGroupItemProps>(
  (
    {
      className,
      value,
      label,
      description,
      disabled: itemDisabled = false,
      required = false,
      id,
      ...props
    },
    ref
  ) => {
    const context = React.useContext(RadioGroupContext);
    const isChecked = context.value === value;
    const isDisabled = context.disabled || itemDisabled;
    const radioId = id || `radio-${React.useId()}`;

    const handleChange = () => {
      if (!isDisabled) {
        context.onValueChange?.(value);
      }
    };

    return (
      <div className="space-y-2">
        <div className="flex items-start space-x-2">
          <div className="relative flex items-center">
            <input
              type="radio"
              ref={ref}
              id={radioId}
              name={context.name}
              value={value}
              checked={isChecked}
              onChange={handleChange}
              disabled={isDisabled}
              required={context.required || required}
              className={cn(
                // Base styles
                'peer h-4 w-4 shrink-0 rounded-full border border-primary ring-offset-background',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
                'disabled:cursor-not-allowed disabled:opacity-50',
                // Brazilian market: larger touch targets
                'min-h-[20px] min-w-[20px]',
                // Custom radio appearance
                'appearance-none cursor-pointer',
                className
              )}
              aria-describedby={description ? `${radioId}-description` : undefined}
              aria-invalid={props['aria-invalid']}
              {...props}
            />

            {/* Custom radio visual */}
            <div
              className={cn(
                'absolute inset-0 flex items-center justify-center pointer-events-none',
                'border rounded-full',
                isChecked ? 'border-primary bg-primary' : 'border-input bg-background',
                isDisabled && 'opacity-50 cursor-not-allowed',
                'min-h-[20px] min-w-[20px]' // Match input size
              )}
            >
              {isChecked && <div className="h-2 w-2 rounded-full bg-primary-foreground" />}
            </div>
          </div>

          {label && (
            <label
              htmlFor={radioId}
              className={cn(
                'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
                isDisabled && 'cursor-not-allowed',
                required && 'after:content-["*"] after:ml-0.5 after:text-destructive'
              )}
            >
              {label}
            </label>
          )}
        </div>

        {description && (
          <p id={`${radioId}-description`} className="text-sm text-muted-foreground pl-6">
            {description}
          </p>
        )}
      </div>
    );
  }
);

RadioGroupItem.displayName = 'RadioGroupItem';

export { RadioGroup, RadioGroupItem };
export default RadioGroup;
