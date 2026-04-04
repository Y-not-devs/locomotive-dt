import { RouterProvider, createBrowserRouter } from "react-router-dom";

import { CabinPage } from "@/pages/cabin/ui/CabinPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <CabinPage />
  }
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
