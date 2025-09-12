import React from "react";
import ReactDOM from "react-dom/client";
import { ChakraProvider, createSystem } from "@chakra-ui/react";
import App from "./App";

const system = createSystem();

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <ChakraProvider value={system}>
      <App />
    </ChakraProvider>
  </React.StrictMode>
);

