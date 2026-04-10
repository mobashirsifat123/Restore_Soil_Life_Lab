import { redirect } from "next/navigation";

import { AdminSidebar } from "@/components/admin/AdminSidebar";
import { getServerSession } from "@/lib/server-session";

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const session = await getServerSession();

  if (!session) {
    redirect("/login");
  }

  if (!session.user.roles.includes("org_admin")) {
    redirect("/dashboard");
  }

  return (
    <div className="min-h-screen bg-[#0a1208] flex">
      <AdminSidebar />
      <main className="min-h-screen flex-1 overflow-y-auto pt-20 md:ml-64 md:pt-0">{children}</main>
    </div>
  );
}
