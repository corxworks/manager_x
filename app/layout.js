import "./globals.css";


export const metadata = {
  title: "Manager X | CORX",
  description:
    "Your AI Creator Manager. Manage deals, emails, tasks, meetings, files and payments in one place.",
};


export default function RootLayout({
  children,
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}