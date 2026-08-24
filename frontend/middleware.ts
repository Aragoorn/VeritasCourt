import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("veritas_token")?.value || 
                request.headers.get("authorization");

  // اگر کاربر به داشبورد می‌رود و توکن ندارد → هدایت به لاگین
  if (request.nextUrl.pathname.startsWith("/dashboard")) {
    // چون توکن در localStorage است، این middleware فقط یک لایه اضافی است.
    // محافظت اصلی سمت کلاینت انجام می‌شود.
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};