import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";

export function useConfirmAction() {
  const confirm = useConfirm();
  const toast = useToast();

  function confirmAction({
    message,
    header = "Confirm Action",
    icon = "pi pi-info-circle",
    acceptLabel = "Confirm",
    rejectLabel = "Cancel",
    severity = "danger",
    onAccept,
    onReject,
  }: {
    message: string;
    header?: string;
    icon?: string;
    acceptLabel?: string;
    rejectLabel?: string;
    severity?: "danger" | "secondary" | "warning" | "success" | "primary";
    onAccept: () => void;
    onReject?: () => void;
    successMessage?: string;
  }) {
    confirm.require({
      message,
      header,
      icon,
      rejectLabel,
      rejectProps: {
        label: rejectLabel,
        severity: "secondary",
        outlined: true,
      },
      acceptProps: {
        label: acceptLabel,
        severity,
      },
      accept: () => {
        onAccept();
      },
      reject: () => onReject?.(),
    });
  }

  return { confirmAction };
}
