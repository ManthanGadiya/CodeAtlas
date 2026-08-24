"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuthContext } from "@/components/auth-context";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/problems", label: "Practice" },
];

export function NavBar() {
  const router = useRouter();
  const pathname = usePathname();
  const { student, setStudent } = useAuthContext();

  async function handleLogout() {
    try {
      await api.logout();
    } catch {
      // Backend unreachable — clear the client session anyway so the UI
      // reflects reality the user can act on.
    }
    setStudent(null);
    router.replace("/login");
  }

  return (
    <header className="border-b border-neutral-200 bg-white">
      <nav className="mx-auto flex max-w-5xl items-center gap-6 px-6 py-3">
        <Link href="/" className="font-semibold tracking-tight">
          CodeAtlas <span aria-hidden>🧭</span>
        </Link>
        {student !== null &&
          LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={
                pathname === link.href
                  ? "text-sm font-medium text-neutral-900 underline underline-offset-4"
                  : "text-sm text-neutral-500 hover:text-neutral-900"
              }
            >
              {link.label}
            </Link>
          ))}
        <span className="ml-auto text-sm text-neutral-500">
          {student ? student.email : null}
        </span>
        {student && (
          <button
            onClick={handleLogout}
            className="text-sm text-neutral-500 hover:text-neutral-900"
          >
            Log out
          </button>
        )}
      </nav>
    </header>
  );
}
