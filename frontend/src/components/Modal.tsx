import React, { useEffect, useState } from 'react';
import { useNotifications, type Notification } from '../context/NotificationContext';

interface Message {
    type: 'system' | 'User' | 'Agent' | 'typing' | 'progress' | 'auth_success' | 'error' | 'conversation_started';
}

export function NotificationContainer() {
    const { notifications, removeNotification } = useNotifications();

    const getNotificationStyles = (type: Notification['type']) => {
        const baseStyles = "mb-3 p-4 rounded-lg border shadow-lg transition-all duration-300 ease-in-out transform";

        switch (type) {
            case 'success':
            case 'auth_success':
                return `${baseStyles} bg-zinc-950 border-green-700 text-green-100`;
            case 'error':
                return `${baseStyles} bg-zinc-950 border-red-700 text-red-100`;
            case 'warning':
                return `${baseStyles} bg-zinc-950 border-yellow-700 text-yellow-100`;
            case 'info':
            case 'system':
                return `${baseStyles} bg-zinc-950 border-blue-700 text-blue-100`;
            case 'Agent':
                return `${baseStyles} bg-zinc-950 border-purple-700 text-purple-100`;
            case 'progress':
                return `${baseStyles} bg-zinc-950 border-zinc-700 text-zinc-100 animate-pulse`;
            default:
                return `${baseStyles} bg-zinc-950 border-zinc-700 text-zinc-100`;
        }
    };

    if (notifications.length === 0) return null;

    return (
        <div className="fixed bottom-5 right-[-5rem] z-50 max-w-sm w-full">
            {notifications.map((notification) => (
                <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onClose={() => removeNotification(notification.id)}
                    className={getNotificationStyles(notification.type)}
                />
            ))}
        </div>
    );
}

interface NotificationItemProps {
    notification: Notification;
    onClose: () => void;
    className: string;
}

function NotificationItem({ notification, onClose, className }: NotificationItemProps) {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // Trigger entrance animation
        const timer = setTimeout(() => setIsVisible(true), 0);
        return () => clearTimeout(timer);
    }, []);

    const handleClose = () => {
        setIsVisible(false);
        setTimeout(onClose, 300); // Wait for exit animation
    };

    return (
        <div
            className={`${className} ${isVisible ? 'translate-x-0 opacity-100 w-70' : 'translate-x-full opacity-0'}`}
            style={{
                transform: isVisible ? 'translateX(0)' : 'translateX(100%)',
                opacity: isVisible ? 1 : 0
            }}
        >
            <div className="flex justify-between items-center">
                <div className="flex items-start">
                    <div className="text-sm font-medium">
                        {notification.message}
                    </div>
                </div>
                {!notification.persistent && (
                    <button
                        onClick={handleClose}
                        className="ml-3 text-current opacity-70 hover:opacity-100 transition-opacity"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}
            </div>
        </div>
    );
}
