import { useNotifications } from '../context/NotificationContext';

export function useNotification() {
    const { addNotification, removeNotification, clearAllNotifications } = useNotifications();

    const showSuccess = (message: string, duration?: number) => {
        return addNotification({
            type: 'success',
            message,
            duration
        });
    };

    const showError = (message: string, duration?: number) => {
        return addNotification({
            type: 'error',
            message,
            duration
        });
    };

    const showWarning = (message: string, duration?: number) => {
        return addNotification({
            type: 'warning',
            message,
            duration
        });
    };

    const showInfo = (message: string, duration?: number) => {
        return addNotification({
            type: 'info',
            message,
            duration
        });
    };

    const showAgentNotification = (message: string, duration?: number) => {
        return addNotification({
            type: 'Agent',
            message,
            duration
        });
    };

    const showAuthSuccess = (message: string = 'Successfully authenticated!', duration?: number) => {
        return addNotification({
            type: 'auth_success',
            message,
            duration
        });
    };

    const showProgress = (message: string, persistent: boolean = false) => {
        return addNotification({
            type: 'progress',
            message,
            persistent,
            duration: persistent ? undefined : 10000 // Longer duration for progress
        });
    };

    const showPersistent = (type: 'success' | 'error' | 'warning' | 'info', message: string) => {
        return addNotification({
            type,
            message,
            persistent: true
        });
    };

    return {
        showSuccess,
        showError,
        showWarning,
        showInfo,
        showAgentNotification,
        showAuthSuccess,
        showProgress,
        showPersistent,
        removeNotification,
        clearAllNotifications
    };
}