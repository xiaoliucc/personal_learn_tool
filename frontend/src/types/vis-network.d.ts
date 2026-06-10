/** vis-network 类型声明 */
declare module 'vis-network' {
  export class Network {
    constructor(container: HTMLElement, data: any, options?: any)
    destroy(): void
    on(event: string, callback: (params: any) => void): void
    setData(data: any): void
    setOptions(options: any): void
    fit(): void
  }
}
