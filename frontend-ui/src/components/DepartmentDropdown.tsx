import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  JIRA_KEY_TO_DEPARTMENT_LABEL,
  type DepartmentId,
} from "../departmentConfig";

export default function DepartmentDropdown() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleSelect(deptId: DepartmentId) {
    setOpen(false);
    navigate(`/department/${deptId}`);
  }

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="
          text-xs px-4 py-1.5 rounded-full
          border border-slate-300 bg-white/80 text-slate-700
          hover:bg-slate-100 hover:border-slate-400
          transition
          dark:border-slate-600 dark:bg-slate-900/70 dark:text-slate-50
          dark:hover:bg-slate-800
        "
      >
        Departments ▾
      </button>

      {open && (
        <div
          className="
            absolute right-0 mt-2 w-56
            rounded-lg border border-slate-200
            bg-white shadow-lg z-50
            dark:border-slate-700 dark:bg-slate-900
          "
        >
          {(
            Object.entries(
              JIRA_KEY_TO_DEPARTMENT_LABEL
            ) as [DepartmentId, string][]
          ).map(([id, label]) => (
            <button
              key={id}
              onClick={() => handleSelect(id)}
              className="
                block w-full text-left px-4 py-2 text-xs
                text-slate-700 hover:bg-slate-100
                dark:text-slate-200 dark:hover:bg-slate-800
              "
            >
              {label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
